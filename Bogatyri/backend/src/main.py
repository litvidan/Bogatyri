import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import asyncio
import json

from RSSISubscriber import MqttSensorSubscriber
from domain.sensor import Sensor
from domain.freq import FrequencyRequest


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
        return {"status": "success", "message": f"Frequency changed to {request.freq}"}
    except Exception as exception:
        return {"status": "error", "message": str(exception)}


@app.post("/start")
async def start_route():
    try:
        print("Starting success!")
        return {"status": "success", "is_start": True}
    except Exception as exception:
        return {"status": "error", "is_start": False}


@app.post("/stop")
async def stop_route():
    try:
        print("Stopping success!")
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
