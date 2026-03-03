from fastapi import WebSocket, WebSocketDisconnect
from typing import List, Dict, Set
import json
import asyncio


class ConnectionManager:
    """WebSocket connection manager with channel support"""
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        # user_id -> websocket
        self.user_connections: Dict[int, WebSocket] = {}
        # channel -> set of websockets
        self.channel_connections: Dict[str, Set[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, user_id: int = None):
        await websocket.accept()
        self.active_connections.append(websocket)
        
        if user_id:
            self.user_connections[user_id] = websocket
    
    def disconnect(self, websocket: WebSocket, user_id: int = None):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        
        # Remove from user connections
        if user_id and user_id in self.user_connections:
            del self.user_connections[user_id]
        
        # Remove from all channels
        for channel in list(self.channel_connections.keys()):
            if websocket in self.channel_connections[channel]:
                self.channel_connections[channel].discard(websocket)
                if not self.channel_connections[channel]:
                    del self.channel_connections[channel]
    
    def subscribe(self, websocket: WebSocket, channel: str):
        """Subscribe websocket to a channel"""
        if channel not in self.channel_connections:
            self.channel_connections[channel] = set()
        self.channel_connections[channel].add(websocket)
    
    def unsubscribe(self, websocket: WebSocket, channel: str):
        """Unsubscribe websocket from a channel"""
        if channel in self.channel_connections:
            self.channel_connections[channel].discard(websocket)
            if not self.channel_connections[channel]:
                del self.channel_connections[channel]
    
    async def send_to_channel(self, channel: str, message: dict):
        """Send message to all connections in a channel"""
        if channel in self.channel_connections:
            disconnected = []
            for websocket in self.channel_connections[channel]:
                try:
                    await websocket.send_json(message)
                except Exception:
                    disconnected.append(websocket)
            
            # Clean up disconnected
            for ws in disconnected:
                self.channel_connections[channel].discard(ws)
    
    async def send_personal_message(self, message: dict, websocket: WebSocket):
        try:
            await websocket.send_json(message)
        except Exception:
            pass
    
    async def send_to_user(self, user_id: int, message: dict):
        """Send message to specific user"""
        if user_id in self.user_connections:
            await self.send_personal_message(message, self.user_connections[user_id])
    
    async def broadcast(self, message: dict):
        """Broadcast to all connections"""
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception:
                disconnected.append(connection)
        
        for ws in disconnected:
            self.active_connections.remove(ws)
    
    def get_connection_count(self) -> int:
        return len(self.active_connections)
    
    def get_channel_count(self, channel: str) -> int:
        return len(self.channel_connections.get(channel, set()))


manager = ConnectionManager()


async def websocket_endpoint(websocket: WebSocket, token: str = None):
    """WebSocket endpoint for real-time communication"""
    user_id = None
    
    # Authenticate if token provided
    if token:
        from app.core.security import decode_token
        payload = decode_token(token)
        if payload:
            user_id = payload.get("sub")
    
    await manager.connect(websocket, user_id)
    
    try:
        await websocket.send_json({
            "type": "connected",
            "status": "ok",
            "user_id": user_id
        })
        
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            message_type = message.get("type")
            
            if message_type == "ping":
                await websocket.send_json({"type": "pong"})
            
            elif message_type == "subscribe":
                channel = message.get("channel")
                if channel:
                    manager.subscribe(websocket, channel)
                    await websocket.send_json({
                        "type": "subscribed",
                        "channel": channel
                    })
            
            elif message_type == "unsubscribe":
                channel = message.get("channel")
                if channel:
                    manager.unsubscribe(websocket, channel)
                    await websocket.send_json({
                        "type": "unsubscribed",
                        "channel": channel
                    })
    
    except WebSocketDisconnect:
        manager.disconnect(websocket, user_id)
    except Exception as e:
        print(f"WebSocket error: {e}")
        manager.disconnect(websocket, user_id)


# Notification helpers
async def notify_new_order(order_data: dict):
    """Notify about new order - broadcast to all cleaners"""
    await manager.broadcast({
        "type": "new_order",
        "data": order_data
    })


async def notify_order_update(order_id: int, status: str, cleaner_id: int = None, host_phone: str = None):
    """Notify about order status change"""
    # Send to specific cleaner
    if cleaner_id:
        await manager.send_to_user(cleaner_id, {
            "type": "order_update",
            "data": {"order_id": order_id, "status": status}
        })
    
    # Send to order channel
    await manager.send_to_channel(f"order:{order_id}", {
        "type": "order_update",
        "data": {"order_id": order_id, "status": status}
    })


async def notify_cleaner_assigned(cleaner_id: int, order_data: dict):
    """Notify cleaner they got a new order"""
    await manager.send_to_user(cleaner_id, {
        "type": "order_assigned",
        "data": order_data
    })


async def notify_host_order_completed(host_phone: str, order_data: dict):
    """Notify host that order is completed"""
    # Broadcast to host's channel
    await manager.send_to_channel(f"host:{host_phone}", {
        "type": "order_completed",
        "data": order_data
    })
