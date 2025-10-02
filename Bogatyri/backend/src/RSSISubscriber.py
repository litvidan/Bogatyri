import json
import paho.mqtt.client as mqtt
from pydantic import BaseModel


class Sensor(BaseModel):
    name: str
    rssi: int
    is_running: bool = True


class MqttSensorSubscriber:
    def __init__(self, broker: str = "localhost", port: int = 1883, topic: str = "sensors/data"):
        self.broker = broker
        self.port = port
        self.topic = topic
        self.client = mqtt.Client()
        self.sensors: dict[str, Sensor] = {}  # храним по имени

        # назначаем колбэки
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print(f"[MQTT] Connected to {self.broker}:{self.port}, subscribed to '{self.topic}'")
            client.subscribe(self.topic)
        else:
            print(f"[MQTT] Connection failed with code {rc}")

    def on_message(self, client, userdata, msg):
        try:
            payload = msg.payload.decode("utf-8")
            data = json.loads(payload)        # ожидаем JSON от датчика
            sensor = Sensor(**data)           # валидация через pydantic
            self.sensors[sensor.name] = sensor  # обновление/добавление сенсора
            self.process_sensor(sensor)
        except Exception as e:
            print(f"[MQTT] Error processing message: {e}")

    def process_sensor(self, sensor: Sensor):
        """Здесь можно обрабатывать новые данные от сенсора"""
        print(f"[DATA] {sensor.name}: RSSI={sensor.rssi}, Running={sensor.is_running}")

    def get_sensors(self) -> list[Sensor]:
        """Вернуть список всех сенсоров"""
        return list(self.sensors.values())

    def run(self):
        print("[MQTT] Starting subscriber...")
        self.client.connect(self.broker, self.port, 60)
        self.client.loop_forever()
