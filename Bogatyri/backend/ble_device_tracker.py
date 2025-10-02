import time
import bluetooth
import ubinascii
from micropython import const

_IRQ_SCAN_RESULT = const(5)
_IRQ_SCAN_DONE = const(6)

class BLEDeviceTracker:
    def __init__(self, scan_duration):
        print("Initializing BLE")
        self.bt = bluetooth.BLE()
        self.bt.active(True)
        self.bt.irq(self.bt_irq)
        print("BLE initialized")

        self.scan_duration = scan_duration  # время сканирования в мс

        # Словарь для хранения устройств: ключ - MAC, значения - dict с именем, rssi
        self.devices = {}

        self.scanning = False
        print("Finished BLEDeviceTracker constructor")

    def decode_name(self, adv_data):
        i = 0
        name = None

        while i < len(adv_data):
            length = adv_data[i]
            if length == 0:
                break
            if i + length >= len(adv_data):
                break
            ad_type = adv_data[i + 1]

            if ad_type == 0x08 or ad_type == 0x09:
                start = i + 2
                end = start + length - 1
                try:
                    name = bytes(adv_data[start:end]).decode('utf-8')
                except Exception:
                    name = None
                break
            i += length + 1
        return name

    def bt_irq(self, event, data):
	    if event == _IRQ_SCAN_RESULT:
	        addr_type, addr, adv_type, rssi, adv_data = data
	        mac = ubinascii.hexlify(addr, ':').decode().upper()
	        name = self.decode_name(adv_data)
	        if name is None:
	            # Игнорируем устройства без имени
	            return
	        else:
	            # Добавляем новое устройство или обновляем существующее
	            self.devices[mac] = {
	                'name': name,
	                'rssi': rssi
	            }
	    elif event == _IRQ_SCAN_DONE:
	        self.scanning = False
	        print("Scan complete")

    def start_scan(self):
    	print("Start scanning")
        self.devices.clear()
        self.scanning = True
        self.bt.gap_scan(self.scan_duration, 0, 0, True)
        print("Finished scanning")

    def print_devices(self):
        print("Tracked devices:")
        now = time.time()
        for mac, dev in self.devices.items():
            if(dev['name'] != 'Unknown'):
            	print(f"{dev['name']} RSSI: {-dev['rssi']}")
        print("-----")

    def run(self):
    	print("Start BLEDeviceTracker running")
        while True:
            self.start_scan()
            while self.scanning:
                time.sleep_ms(100)
            self.print_devices()




tracker = BLEDeviceTracker(scan_duration=1000)
tracker.run()
