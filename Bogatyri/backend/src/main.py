import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import json
import random
import paho.mqtt.client as mqtt

from src.models.schemas import FrequencyRequest, BeaconRequest, Message
from src.services.monitor_state import MonitorState
from src.services.websocket_connection_manager import ConnectionManager

app = FastAPI(title="Wanderer API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

monitor = MonitorState()
manager = ConnectionManager()


class WandererSimulator:
    def __init__(self):
        self.coords = {}
        self.generate_coords()

    def generate_coords(self):
        self.coords = {"x": round(random.uniform(1, 9), 2), "y": round(random.uniform(1, 6), 2)}

    def update_coords(self):
        self.coords["x"] = round(max(0.5, min(9.5, self.coords["x"] + random.uniform(-3.3, 3.3))), 2)
        self.coords["y"] = round(max(0.5, min(6.5, self.coords["y"] + random.uniform(-3.3, 3.3))), 2)
        return self.coords


class WandererMQTTSubscriber:
    def __init__(self):
        self.broker = "localhost"
        self.port = 1883
        self.topic = "data/devices"
        self.client = mqtt.Client()
        self.client.on_message=self.on_message
        self.client.connect(self.broker, self.port, 60)

        self.devices_data = {}

    def on_message(self, client, userdata, msg):

        msg = Message(**msg.payload().decode())
        self.devices_data = msg.data


    def on_connect(client, userdata, flags, rc):
        print("Подключено к брокеру, код возврата:", rc)
        # client.subscribe(self.topic)

    def update_coords(self):
        self.coords["x"] = round(max(0.5, min(9.5, self.coords["x"] + random.uniform(-3.3, 3.3))), 2)
        self.coords["y"] = round(max(0.5, min(6.5, self.coords["y"] + random.uniform(-3.3, 3.3))), 2)
        return self.coords
     


wanderer_simulator = WandererSimulator()


@app.websocket("/ws/wanderer")
async def websocket_wanderer(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        await websocket.send_text(json.dumps(wanderer_simulator.coords))
        print("Client connected")

        while True:
            coords_data = wanderer_simulator.update_coords()
            await websocket.send_text(json.dumps(coords_data))
            await asyncio.sleep(2)

    except WebSocketDisconnect:
        manager.disconnect(websocket)
        print("Client disconnected")
    except Exception as exception:
        print(f"WebSocket error: {exception}")
        manager.disconnect(websocket)

@app.post("/start")
async def start_route(request: FrequencyRequest):
    try:
        monitor.start_monitoring(request.freq)
        print(f"Starting success!")
        return {"status": "success", "is_start": True}
    except Exception as exception:
        print(f"Starting error: {exception}")
        return {"status": "error", "is_start": False}

@app.post("/beacons")
async def add_beacons(request: BeaconRequest):
    try:
        monitor.add_beacons(request.beacons)
        print(f"Starting success!")
        return {"status": "success"}
    except Exception as exception:
        print(f"Starting error: {exception}")
        return {"status": "error"}

@app.post("/stop")
async def stop_route():
    try:
        monitor.stop_monitoring()
        print(f"Stopping success!")
        return {"status": "success", "is_stop": True}
    except Exception as exception:
        print(f"Stopping error: {exception}")
        return {"status": "error", "is_stop": False}

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        ws="auto"
    )