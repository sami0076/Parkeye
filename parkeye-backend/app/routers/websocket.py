"""WebSocket router - ws://.../ws/occupancy."""
import asyncio
import json

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import AsyncSessionLocal
from app.services.occupancy import get_all_current_occupancy

router = APIRouter(tags=["websocket"])


class ConnectionManager:
    """Manage WebSocket connections."""

    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections[:]:
            try:
                await connection.send_text(message)
            except Exception:
                self.disconnect(connection)


manager = ConnectionManager()


async def broadcast_loop():
    """Every 30 seconds, broadcast occupancy to all connected clients."""
    while True:
        await asyncio.sleep(30)
        async with AsyncSessionLocal() as session:
            occupancy = await get_all_current_occupancy(session)
        payload = json.dumps(occupancy)
        await manager.broadcast(payload)


@router.websocket("/ws/occupancy")
async def websocket_occupancy(websocket: WebSocket):
    """Stream occupancy data every 30 seconds to connected clients."""
    await manager.connect(websocket)
    try:
        # Send initial data immediately
        async with AsyncSessionLocal() as session:
            occupancy = await get_all_current_occupancy(session)
        await websocket.send_text(json.dumps(occupancy))

        # Keep connection alive, receive any messages (client can ping)
        while True:
            try:
                data = await asyncio.wait_for(websocket.receive_text(), timeout=35)
                # Echo or ignore - main updates come from broadcast
            except asyncio.TimeoutError:
                # Send current data on timeout (fallback if broadcast misses)
                async with AsyncSessionLocal() as session:
                    occupancy = await get_all_current_occupancy(session)
                await websocket.send_text(json.dumps(occupancy))
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception:
        manager.disconnect(websocket)
        raise
