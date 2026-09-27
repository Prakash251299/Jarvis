from __future__ import annotations

import asyncio
from typing import Dict, Optional, Set
from fastapi import WebSocket
from loguru import logger

class ConnectionManager:
    """Manages active WebSocket connections per conversation session."""

    def __init__(self):
        self._active_connections: Dict[str, Set[WebSocket]] = {}
        self._lock = asyncio.Lock()

    async def connect(self, conversation_id: str, websocket: WebSocket):
        await websocket.accept()
        async with self._lock:
            if conversation_id not in self._active_connections:
                self._active_connections[conversation_id] = set()
            self._active_connections[conversation_id].add(websocket)
        logger.info("WebSocket connected for conversation: {}", conversation_id)

    async def disconnect(self, conversation_id: str, websocket: WebSocket):
        async with self._lock:
            if conversation_id in self._active_connections:
                self._active_connections[conversation_id].discard(websocket)
                if not self._active_connections[conversation_id]:
                    del self._active_connections[conversation_id]
        logger.info("WebSocket disconnected for conversation: {}", conversation_id)

    async def send_json(self, conversation_id: str, message: dict):
        async with self._lock:
            sockets = list(self._active_connections.get(conversation_id, []))

        for socket in sockets:
            try:
                await socket.send_json(message)
            except Exception as e:
                logger.warning("Error sending JSON to client in {}: {}", conversation_id, e)

    async def send_bytes(self, conversation_id: str, data: bytes):
        async with self._lock:
            sockets = list(self._active_connections.get(conversation_id, []))

        for socket in sockets:
            try:
                await socket.send_bytes(data)
            except Exception as e:
                logger.warning("Error sending bytes to client in {}: {}", conversation_id, e)

    async def broadcast(self, message: dict):
        async with self._lock:
            all_sockets = [s for sockets in self._active_connections.values() for s in sockets]

        for socket in all_sockets:
            try:
                await socket.send_json(message)
            except Exception as e:
                logger.warning("Error broadcasting message: {}", e)

    def is_connected(self, conversation_id: str) -> bool:
        return conversation_id in self._active_connections and bool(self._active_connections[conversation_id])

manager = ConnectionManager()
