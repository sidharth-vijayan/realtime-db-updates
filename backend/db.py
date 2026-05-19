import asyncpg
import asyncio
import json
import os
from dotenv import load_dotenv

load_dotenv()  

connected_clients = set()


async def handle_notification(connection, pid, channel, payload):
    """
    This function is called automatically by asyncpg
    whenever PostgreSQL fires a NOTIFY on 'orders_channel'.
    
    It takes the raw JSON payload and sends it to every
    connected WebSocket client.
    """
    print(f"[DB] Change detected: {payload}")

    if connected_clients:
        for client in list(connected_clients):
            try:
                await client.send_text(payload)
            except Exception:
                connected_clients.discard(client)


async def listen_to_db():
    """
    Opens a persistent connection to PostgreSQL and
    starts listening on 'orders_channel'.
    
    This runs forever in the background as long as
    the server is running.
    """
    conn = await asyncpg.connect(
        host=os.getenv("DB_HOST"),
        port=int(os.getenv("DB_PORT")),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )

    await conn.add_listener("orders_channel", handle_notification)

    print("[DB] Listening for changes on 'orders_channel'...")

    while True:
        await asyncio.sleep(1)