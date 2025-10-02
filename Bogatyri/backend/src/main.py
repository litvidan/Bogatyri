import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import json
from src.RSSISubscriber import MqttSensorSubscriber
from src.models.schemas import FrequencyRequest, BeaconRequest
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

@app.post("/start")
async def start_route(request: FrequencyRequest):
    try:
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
