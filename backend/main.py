import asyncio
import json
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from contextlib import asynccontextmanager
from backend.db import connected_clients, listen_to_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    This runs when the server starts up.
    It kicks off the DB listener in the background
    so it runs alongside the web server.
    """
    asyncio.create_task(listen_to_db())
    print("[Server] Started. DB listener running in background.")
    yield  
    print("[Server] Shutting down.")


app = FastAPI(lifespan=lifespan)


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    Clients connect here via WebSocket.
    We add them to connected_clients so db.py can reach them.
    """
    await websocket.accept()
    connected_clients.add(websocket)
    print(f"[WS] Client connected. Total: {len(connected_clients)}")

    try:
        while True:
            await websocket.receive_text()

    except WebSocketDisconnect:
        connected_clients.discard(websocket)
        print(f"[WS] Client disconnected. Total: {len(connected_clients)}")