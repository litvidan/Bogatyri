import paho.mqtt.client as mqtt
import json
import threading

from src.services.controller_listener import run_mpremote

broker = "mqtt"
port = 1883
topic = "beacons"

def mqtt_publish_lines(update_time_seconds=1, stop_event: threading.Event = None):
    client = mqtt.Client()
    client.connect(broker, port, 60)
    client.loop_start()

    def process_line(line):
        line = line.strip()
        if not line:
            return

        parts = line.split(maxsplit=1)
        if len(parts) < 2:
            print("Неверный формат строки:", line)
            return

        name, number_str = parts[0], parts[1]

        try:
            number = int(number_str)
        except ValueError:
            print("Не удалось преобразовать число:", number_str)
            return

        payload = json.dumps({
            "name": name,
            "rssi": number
        })

        print(payload)
        client.publish(topic, payload)

        if stop_event and stop_event.is_set():
            raise KeyboardInterrupt

    try:
        run_mpremote(update_time_seconds, line_callback=process_line)
    except KeyboardInterrupt:
        print("Monitoring stopped by stop_event")

    client.loop_stop()
    client.disconnect()
