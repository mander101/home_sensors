import asyncio
from bleak import BleakScanner, BleakClient
from bleparser import BleParser
from atc_mi_interface import native_temp_hum_v_values, native_comfort_values

gatt_dict = {
    "atc1441": {
        "gatt": '0000181a-0000-1000-8000-00805f9b34fb',  # Environmental Sensing
        "length": 13,
        "header": bytes.fromhex("161a18"),
    },
    "custom": {
        "gatt": '0000181a-0000-1000-8000-00805f9b34fb',
        "length": 15,
        "header": bytes.fromhex("161a18"),
    },
    "custom_enc": {
        "gatt": '0000181a-0000-1000-8000-00805f9b34fb',
        "length": 11,
        "header": bytes.fromhex("161a18"),
    },
    "atc1441_enc": {
        "gatt": '0000181a-0000-1000-8000-00805f9b34fb',
        "length": 8,
        "header": bytes.fromhex("161a18"),
    },
    "mi_like": {
        "gatt": '0000fe95-0000-1000-8000-00805f9b34fb',  # Xiaomi Inc.
        "length": None,
        "header": bytes.fromhex("1695fe"),
    },
    "bt_home": {
        "gatt": '0000181c-0000-1000-8000-00805f9b34fb',  # SERVICE_UUID_USER_DATA, HA_BLE, no security
        "length": None,
        "header": bytes.fromhex("161c18"),
    },
    "bt_home_enc": {
        "gatt": '0000181e-0000-1000-8000-00805f9b34fb',
        "length": None,
        "header": bytes.fromhex("161e18"),
    },
    "bt_home_v2": {
        "gatt": '0000fcd2-0000-1000-8000-00805f9b34fb',
        "length": None,
        "header": bytes.fromhex("16d2fc"),
    }
}


def atc_mi_advertising_format(advertisement_data):
    if not advertisement_data.service_data:
        return "", ""
    invalid_length = None
    for t in gatt_dict.keys():
        gatt_d = gatt_dict[t]
        if gatt_d["gatt"] in advertisement_data.service_data:
            payload = advertisement_data.service_data[gatt_d["gatt"]]
            if gatt_d["length"] and len(payload) != gatt_d["length"]:
                invalid_length = len(payload)
                continue
            header = gatt_d["header"]
            return t, bytes([len(header) + len(payload)]) + header + payload
    if invalid_length is not None:
        return "Unknown-length-" + str(invalid_length), ""
    return "Unknown", ""
    
async def scanner(stop_event):
    scanner = BleakScanner()
    scanner.register_detection_callback(detection_callback)
    await scanner.start()
    
    while not stop_event.is_set():
        await asyncio.sleep(0.1)  # Sleep briefly to allow other tasks to run
    
    await scanner.stop()

async def detection_callback(device, advertisement_data):
    if device.name == "temp_laundry_door":
        format_label, adv_data = atc_mi_advertising_format(advertisement_data)
        if "Unknown" in format_label:
            logging.warning(
                "mac: %s. %s advertisement: %s. RSSI: %s",
                device.address, format_label, advertisement_data,
                advertisement_data.rssi)
            return

        print(
            "mac: %s. %s advertisement: %s. RSSI: %s",
            device.address, format_label, advertisement_data,
            advertisement_data.rssi)

async def monitor_keyboard(stop_event):
    loop = asyncio.get_running_loop()
    await loop.run_in_executor(None, input, "Press 'q' to stop scanning...\n")
    stop_event.set()

async def ble_scanner_main():
    stop_event = asyncio.Event()
    
    # Create scanner and keyboard monitoring tasks
    scanner_task = asyncio.create_task(scanner(stop_event))
    keyboard_task = asyncio.create_task(monitor_keyboard(stop_event))

    # Wait for either task to complete
    await asyncio.wait([scanner_task, keyboard_task], return_when=asyncio.FIRST_COMPLETED)
    
    # Ensure both tasks are cancelled/stopped
    stop_event.set()
    await scanner_task
    await keyboard_task

async def ble_home_get_data():
  mac_address = "A4:C1:38:1A:67:99"
  _UUID_NAME     ="00002a00-0000-1000-8000-00805f9b34fb"
  _UUID_FIRM_BATT="00002a19-0000-1000-8000-00805f9b34fb"
  CHARACTERISTIC_UUID="ebe0ccc1-7a0a-4b0c-8a1a-6ff2997da3a6"
  
  valid_string_characteristics = [2, 13, 15, 17, 19, 21, 23, 95]
  valid_bytes_characteristics = [26, 30, 33, 34, 36, 37, 57]
  humidity_char = 36
  temperature_char = 33
  temperature_celcius_char = 30
  native_temp_hum_v_char = 53
  native_comfort_char = 66
  for times in range(20):
      try:
          async with BleakClient(mac_address, timeout=60.0) as client:
              for service in client.services:
                  for char in service.characteristics:
                      name_bytes = await client.read_gatt_char(char)
                      if char.handle in valid_bytes_characteristics:
                          print(char.handle, service.description, "-", char.description, "- Value:", name_bytes.hex(" "), flush=True)
                      if char.handle in valid_string_characteristics:
                          print(char.handle, service.description, "-", char.description, ":", name_bytes.decode(), flush=True)
                                 
                      if char.handle == temperature_char:
                        value = ((name_bytes[1] << 8) + name_bytes[0])/100
                        print(char.description, ":", value, flush=True)
                      if char.handle == humidity_char:
                                               
                        value = ((name_bytes[1] << 8) + name_bytes[0])/100
                        print(char.description, ":", value, flush=True)
                      if char.handle == temperature_celcius_char:
                        value = ((name_bytes[1] << 8) + name_bytes[0])/10
                        print(char.description, ":", value, flush=True)                                                                                                
                      if char.handle == native_temp_hum_v_char:
                          print(char.handle, char.description, ":", native_temp_hum_v_values.parse(name_bytes))
                      if char.handle == native_comfort_char:
                          print(char.handle, char.description, ":", native_comfort_values.parse(name_bytes))
                          
                          
              break
      except Exception as e:
          print(f"Retrying... ({e})")
            

if __name__ == "__main__":
    #asyncio.run(ble_scanner_main())
    asyncio.run(ble_home_get_data())