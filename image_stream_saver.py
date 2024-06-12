import os
import datetime
import asyncio
from bleak import BleakClient, BleakScanner

# Define BLE UUIDs (should match the Arduino code)
SERVICE_UUID = "19B10000-E8F2-537E-4F6C-D104768A1214"
PHOTO_CHAR_UUID = "19B10005-E8F2-537E-4F6C-D104768A1214"

# Directory to save images
images_dir = "images"
if not os.path.exists(images_dir):
    os.makedirs(images_dir)

photo_data = bytearray()
receiving_photo = False

def save_photo():
    global photo_data
    filename = datetime.datetime.now().strftime("%Y%m%d_%H%M%S.jpg")
    filepath = os.path.join(images_dir, filename)
    with open(filepath, "wb") as f:
        f.write(photo_data)
    print(f"Photo saved to {filepath}")

def handle_notification(sender, data):
    global photo_data, receiving_photo
    if data[0] == 0xFF and data[1] == 0xFF:
        save_photo()
        receiving_photo = False
        photo_data = bytearray()
    else:
        if not receiving_photo:
            receiving_photo = True
            photo_data = bytearray()
        photo_data.extend(data[2:])

async def main():
    device_address = None

    # Scan for devices
    devices = await BleakScanner.discover()
    for device in devices:
        print(f"Found device: {device.address} - {device.name}")
        if device.name == "OpenGlass":  # Replace with your device name
            device_address = device.address
            break

    if not device_address:
        print("Device not found")
        return

    async with BleakClient(device_address) as client:
        print(f"Connected to {device_address}")

        # Enable notifications
        await client.start_notify(PHOTO_CHAR_UUID, handle_notification)
        print("Notifications enabled. Waiting for image data...")

        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            print("Disconnecting...")
            await client.stop_notify(PHOTO_CHAR_UUID)

if __name__ == "__main__":
    asyncio.run(main())
