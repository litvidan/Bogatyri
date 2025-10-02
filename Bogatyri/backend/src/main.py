from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import asyncio
import json
import random
import time

app = FastAPI(title="Wanderer API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class FrequencyRequest(BaseModel):
    freq: int

class ConnectionManager:
    def __init__(self):
        self.active_connections = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
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

@app.post("/frequency")
async def change_frequensy(request: FrequencyRequest):
    try:
        await change_monitoring_frequency(freq=request.freq)
        return {"status": "success", "message": f"Frequency changed to {request.new_freq}"}
    except Exception as exception:
        print(f"Modification error: {exception}")
        return {"status": "error", "message": str(exception)}

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        ws="auto"
    )