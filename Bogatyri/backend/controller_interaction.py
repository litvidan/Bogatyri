import time
import bluetooth
import time
import ubinascii
from micropython import const

_IRQ_SCAN_RESULT = const(5)
_IRQ_SCAN_DONE = const(6)

def decode_name(adv_data):
    i = 0
    name = None

    while i < len(adv_data):
        length = adv_data[i]
        if length == 0:
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


def bt_irq(event, data):
  if event == _IRQ_SCAN_RESULT:
    # A single scan result.
	addr_type, addr, adv_type, rssi, adv_data = data
	mac = ubinascii.hexlify(addr, ':').decode().upper()
	name = decode_name(adv_data)
	if(name != None): 
		print("DEVICE. name: ", name, " mac: ", mac, " rssi: ", rssi)
  elif event == _IRQ_SCAN_DONE:
    # Scan duration finished or manually stopped.
    print('scan complete')

# Scan for 10s (at 100% duty cycle)
ms_scan = 10000
bt = bluetooth.BLE()
bt.irq(bt_irq)
bt.active(True)
bt.gap_scan(ms_scan, 30000, 30000, True)
time.sleep_ms(ms_scan)