import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import json

from RSSISubscriber import MqttSensorSubscriber
from domain.sensor import Sensor
from domain.freq import FrequencyRequest

import random
import paho.mqtt.client as mqtt

from src.models.schemas import FrequencyRequest, BeaconRequest, Message
from src.services.monitor_state import MonitorState

MQTT_TOPIC = "sensors/frequency"

app = FastAPI(title="Wanderer API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ConnectionManager:
    def __init__(self):
        self.active_connections = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except:
                self.disconnect(connection)

monitor = MonitorState()
manager = ConnectionManager()

# Создаём подписчика MQTT
mqtt_subscriber = MqttSensorSubscriber(
    broker="localhost",
    port=1883,
    topic="sensors/data"
)


# ---- WebSocket ----     

@app.websocket("/ws/wanderer")
async def websocket_wanderer(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        print("Client connected")

        while True:
            sensors_data = mqtt_subscriber.get_sensors()
            await websocket.send_text(json.dumps(sensors_data, ensure_ascii=False))
            await asyncio.sleep(2)

    except WebSocketDisconnect:
        manager.disconnect(websocket)
        print("Client disconnected")
    except Exception as exception:
        print(f"WebSocket error: {exception}")
        manager.disconnect(websocket)


# ---- REST endpoints ----
@app.post("/frequency")
async def change_frequensy(request: FrequencyRequest):
    try:
        # Формируем payload
        payload = {"frequency": request.freq}
        mqtt_subscriber.publish(MQTT_TOPIC, json.dumps(payload))

        return {"status": "success", "message": f"Frequency changed to {request.freq}"}
    except Exception as exception:
        return {"status": "error", "message": str(exception)}


@app.post("/start")
async def start_route(request: FrequencyRequest):
    try:
        print("Starting success!")
        monitor.start_monitoring(request.freq)
        print(f"Starting success!")
        return {"status": "success", "is_start": True}
    except Exception as exception:
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
        print("Stopping success!")
        monitor.stop_monitoring()
        print(f"Stopping success!")
        return {"status": "success", "is_stop": True}
    except Exception as exception:
        return {"status": "error", "is_stop": False}


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
