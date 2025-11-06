"""WebSocket connection manager for real-time communication."""

import asyncio
import json
from datetime import datetime
from typing import Any, Dict, List, Optional, Set

from fastapi import WebSocket, WebSocketDisconnect

from backend.utils.errors import WebSocketError
from backend.utils.logger import get_logger

logger = get_logger(__name__)


class ConnectionManager:
    """
    Manager for WebSocket connections with pub/sub support.
    """
    
    def __init__(self, max_connections: int = 100) -> None:
        """
        Initialize connection manager.
        
        Args:
            max_connections: Maximum number of concurrent connections
        """
        self.active_connections: Dict[str, WebSocket] = {}
        self.user_connections: Dict[str, Set[str]] = {}  # user_id -> set of connection_ids
        self.max_connections = max_connections
        logger.info(f"WebSocket connection manager initialized (max: {max_connections})")
    
    async def connect(self, websocket: WebSocket, connection_id: str, user_id: str) -> None:
        """
        Accept and register a new WebSocket connection.
        
        Args:
            websocket: WebSocket instance
            connection_id: Unique connection identifier
            user_id: User identifier
        
        Raises:
            WebSocketError: If max connections exceeded
        """
        if len(self.active_connections) >= self.max_connections:
            await websocket.close(code=1008, reason="Max connections exceeded")
            raise WebSocketError(
                "Max connections exceeded",
                details={"max": self.max_connections}
            )
        
        await websocket.accept()
        
        self.active_connections[connection_id] = websocket
        
        if user_id not in self.user_connections:
            self.user_connections[user_id] = set()
        self.user_connections[user_id].add(connection_id)
        
        logger.info(
            "WebSocket connection established",
            connection_id=connection_id,
            user_id=user_id,
            total_connections=len(self.active_connections)
        )
        
        # Send connection confirmation
        await self.send_message(connection_id, {
            "type": "connection_established",
            "connection_id": connection_id,
            "timestamp": datetime.utcnow().isoformat()
        })
    
    def disconnect(self, connection_id: str, user_id: str) -> None:
        """
        Remove a WebSocket connection.
        
        Args:
            connection_id: Connection identifier
            user_id: User identifier
        """
        if connection_id in self.active_connections:
            del self.active_connections[connection_id]
        
        if user_id in self.user_connections:
            self.user_connections[user_id].discard(connection_id)
            if not self.user_connections[user_id]:
                del self.user_connections[user_id]
        
        logger.info(
            "WebSocket connection closed",
            connection_id=connection_id,
            user_id=user_id,
            remaining_connections=len(self.active_connections)
        )
    
    async def send_message(self, connection_id: str, message: Dict[str, Any]) -> bool:
        """
        Send message to a specific connection.
        
        Args:
            connection_id: Connection identifier
            message: Message to send
        
        Returns:
            True if sent successfully, False otherwise
        """
        websocket = self.active_connections.get(connection_id)
        if not websocket:
            logger.warning(f"Connection {connection_id} not found")
            return False
        
        try:
            await websocket.send_json(message)
            logger.debug(f"Message sent to {connection_id}", message_type=message.get("type"))
            return True
        except Exception as e:
            logger.error(f"Failed to send message to {connection_id}", error=str(e))
            return False
    
    async def send_to_user(self, user_id: str, message: Dict[str, Any]) -> int:
        """
        Send message to all connections of a user.
        
        Args:
            user_id: User identifier
            message: Message to send
        
        Returns:
            Number of successful sends
        """
        connection_ids = self.user_connections.get(user_id, set())
        if not connection_ids:
            logger.debug(f"No connections found for user {user_id}")
            return 0
        
        success_count = 0
        for connection_id in list(connection_ids):  # Use list() to avoid modification during iteration
            if await self.send_message(connection_id, message):
                success_count += 1
        
        logger.info(
            f"Message sent to user {user_id}",
            message_type=message.get("type"),
            connections=len(connection_ids),
            successful=success_count
        )
        
        return success_count
    
    async def broadcast(self, message: Dict[str, Any], exclude: Optional[Set[str]] = None) -> int:
        """
        Broadcast message to all connections.
        
        Args:
            message: Message to broadcast
            exclude: Set of connection IDs to exclude
        
        Returns:
            Number of successful sends
        """
        exclude = exclude or set()
        success_count = 0
        
        for connection_id in list(self.active_connections.keys()):
            if connection_id not in exclude:
                if await self.send_message(connection_id, message):
                    success_count += 1
        
        logger.info(
            "Broadcast message sent",
            message_type=message.get("type"),
            total_connections=len(self.active_connections),
            successful=success_count
        )
        
        return success_count
    
    async def handle_ping(self, connection_id: str) -> None:
        """
        Handle ping message with pong response.
        
        Args:
            connection_id: Connection identifier
        """
        await self.send_message(connection_id, {
            "type": "pong",
            "timestamp": datetime.utcnow().isoformat()
        })
    
    def get_connection_count(self) -> int:
        """Get total number of active connections."""
        return len(self.active_connections)
    
    def get_user_connection_count(self, user_id: str) -> int:
        """Get number of connections for a specific user."""
        return len(self.user_connections.get(user_id, set()))
    
    async def close_all(self) -> None:
        """Close all active connections."""
        logger.info(f"Closing all {len(self.active_connections)} connections")
        
        for connection_id, websocket in list(self.active_connections.items()):
            try:
                await websocket.close()
            except Exception as e:
                logger.error(f"Error closing connection {connection_id}", error=str(e))
        
        self.active_connections.clear()
        self.user_connections.clear()
        logger.info("All connections closed")


# Global connection manager instance
connection_manager = ConnectionManager()
