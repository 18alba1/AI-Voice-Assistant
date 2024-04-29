import streamlit as st
import asyncio
import bleak

# Streamlit app title
st.title('Bluetooth Low Energy Device Discovery')

# Define the UUIDs
SERVICE_UUID = "4fafc201-1fb5-459e-8fcc-c5c9c331914b"
CHARACTERISTIC_UUID = "beb5483e-36e1-4688-b7f5-ea07361b26a8"

# Function to discover BLE devices and print out UUIDs
async def discover_ble_devices():
    scanner = bleak.BleakScanner()
    devices = await scanner.discover()
    return devices

# Function to display discovered devices and their UUIDs
def display_devices(devices):
    st.write("Discovered Bluetooth Low Energy devices:")
    for device in devices:
        # Extract service UUID and characteristic UUID from advertisement data
        service_uuid = device.metadata.get('uuids', [])
        characteristic_uuid = device.metadata.get('characteristics', [])
        
        # Print out device information
        st.write(f"Device Name: {device.name}")
        st.write(f"Service UUIDs: {service_uuid}")
        st.write(f"Characteristic UUIDs: {characteristic_uuid}")
        st.write("")

# Function to connect to a BLE device
async def connect_to_device(device_address):
    async with bleak.BleakClient(device_address) as client:
        await client.connect()  # Connect to the device
        st.write(f"Connected to device: {client.address}")

# Button to start BLE device discovery
if st.button('Start BLE Device Discovery'):
    # Create an event loop
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    # Run the coroutine inside the event loop
    devices = loop.run_until_complete(discover_ble_devices())
    display_devices(devices)

    # Check if "Ecco6" device is in the discovered devices
    for device in devices:
        if device.name == "Ecco6":
            st.write("Found device 'Ecco6'. Attempting to connect...")
            loop.run_until_complete(connect_to_device(device.address))
            break
    else:
        st.write("Device 'Ecco6' not found.")
