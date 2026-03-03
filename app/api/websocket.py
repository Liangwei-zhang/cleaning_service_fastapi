from fastapi import WebSocket, WebSocketDisconnect
from typing import List, Dict
import json
import asyncio


class ConnectionManager:
    """WebSocket connection manager"""
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.user_connections: Dict[int, WebSocket] = {}  # user_id -> websocket
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
    
    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        # Remove from user connections
        for user_id, ws in list(self.user_connections.items()):
            if ws == websocket:
                del self.user_connections[user_id]
    
    async def send_personal_message(self, message: dict, websocket: WebSocket):
        try:
            await websocket.send_json(message)
        except Exception:
            pass
    
    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception:
                pass
    
    def get_connection_count(self) -> int:
        return len(self.active_connections)


manager = ConnectionManager()


async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time communication"""
    await manager.connect(websocket)
    
    try:
        # Authenticate
        await websocket.send_json({"type": "connected", "status": "ok"})
        
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            message_type = message.get("type")
            
            if message_type == "ping":
                await websocket.send_json({"type": "pong"})
            
            elif message_type == "auth":
                # Store user connection
                # token = message.get("token")
                # TODO: Verify token and store user_id
                pass
            
            elif message_type == "subscribe":
                # Subscribe to order updates
                await websocket.send_json({
                    "type": "subscribed",
                    "channel": message.get("channel")
                })
    
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        print(f"WebSocket error: {e}")
        manager.disconnect(websocket)


# Notify all connected clients about new order
async def notify_new_order(order_data: dict):
    await manager.broadcast({
        "type": "new_order",
        "data": order_data
    })


# Notify about order status change
async def notify_order_update(order_id: int, status: str):
    await manager.broadcast({
        "type": "order_update",
        "data": {
            "order_id": order_id,
            "status": status
        }
    })
