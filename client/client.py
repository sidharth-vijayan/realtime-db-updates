import asyncio
import json
import websockets


async def listen():
    uri = "ws://127.0.0.1:8000/ws"
    print("Connecting to server...")

    async with websockets.connect(uri) as websocket:
        print("Connected! Waiting for order updates...\n")

        while True:
            message = await websocket.recv()

            data = json.loads(message)

            print("--- Order Update Received ---")
            print(f"  Operation     : {data['operation']}")
            print(f"  Order ID      : {data['id']}")
            print(f"  Customer      : {data['customer_name']}")
            print(f"  Product       : {data['product_name']}")
            print(f"  Status        : {data['status']}")
            print(f"  Updated At    : {data['updated_at']}")
            print("-----------------------------\n")


asyncio.run(listen())