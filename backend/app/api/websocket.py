from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from typing import Dict, List, Set
import json
import asyncio
from datetime import datetime, timedelta
import logging

from app.database import get_db
from app.auth import get_current_user_ws
from app import models

router = APIRouter()
logger = logging.getLogger(__name__)

# Store active connections
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.user_connections: Dict[str, Set[str]] = {}  # user_id -> connection_ids
        
    async def connect(self, websocket: WebSocket, user_id: str):
        await websocket.accept()
        connection_id = id(websocket)
        self.active_connections[connection_id] = websocket
        
        if user_id not in self.user_connections:
            self.user_connections[user_id] = set()
        self.user_connections[user_id].add(connection_id)
        
        logger.info(f"User {user_id} connected. Total connections: {len(self.active_connections)}")
        
    def disconnect(self, websocket: WebSocket, user_id: str):
        connection_id = id(websocket)
        self.active_connections.pop(connection_id, None)
        
        if user_id in self.user_connections:
            self.user_connections[user_id].discard(connection_id)
            if not self.user_connections[user_id]:
                del self.user_connections[user_id]
        
        logger.info(f"User {user_id} disconnected. Total connections: {len(self.active_connections)}")
    
    async def send_personal_message(self, message: dict, user_id: str):
        """Send message to specific user"""
        if user_id in self.user_connections:
            for connection_id in self.user_connections[user_id]:
                websocket = self.active_connections.get(connection_id)
                if websocket:
                    try:
                        await websocket.send_json(message)
                    except Exception as e:
                        logger.error(f"Error sending to {user_id}: {e}")
    
    async def broadcast(self, message: dict):
        """Send message to all connected users"""
        for websocket in self.active_connections.values():
            try:
                await websocket.send_json(message)
            except Exception as e:
                logger.error(f"Broadcast error: {e}")

manager = ConnectionManager()

# Streak checking task
async def check_streaks_periodically():
    """Background task to check and update streaks"""
    while True:
        await asyncio.sleep(3600)  # Check every hour
        
        # In a real app, you would query database and check streaks
        # For demo, we'll just log
        logger.info("Checking user streaks...")
        
        # Example: Send reminder to users who haven't read today
        # current_time = datetime.utcnow()
        # if current_time.hour == 20:  # 8 PM
        #     await send_evening_reminders()

@router.websocket("/ws/streak")
async def websocket_streak_endpoint(
    websocket: WebSocket,
    token: str = None
):
    """WebSocket for real-time streak updates"""
    if not token:
        await websocket.close(code=1008)
        return
    
    try:
        # Authenticate user
        user = await get_current_user_ws(token)
        if not user:
            await websocket.close(code=1008)
            return
        
        await manager.connect(websocket, str(user.id))
        
        try:
            # Send initial streak data
            await websocket.send_json({
                "type": "streak_update",
                "streak_count": user.streak_count,
                "last_read": user.last_read_date.isoformat() if user.last_read_date else None,
                "message": f"Current streak: {user.streak_count} days"
            })
            
            # Keep connection alive and listen for messages
            while True:
                data = await websocket.receive_text()
                message = json.loads(data)
                
                if message.get("type") == "ping":
                    await websocket.send_json({"type": "pong", "timestamp": datetime.utcnow().isoformat()})
                
                elif message.get("type") == "reading_started":
                    await manager.send_personal_message({
                        "type": "reading_progress",
                        "user_id": str(user.id),
                        "book_id": message.get("book_id"),
                        "action": "started",
                        "timestamp": datetime.utcnow().isoformat()
                    }, str(user.id))
                
                elif message.get("type") == "reading_ended":
                    await manager.send_personal_message({
                        "type": "reading_progress",
                        "user_id": str(user.id),
                        "book_id": message.get("book_id"),
                        "duration_minutes": message.get("duration", 0),
                        "pages_read": message.get("pages", 0),
                        "action": "ended",
                        "timestamp": datetime.utcnow().isoformat(),
                        "streak_updated": True
                    }, str(user.id))
                    
        except WebSocketDisconnect:
            manager.disconnect(websocket, str(user.id))
            
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        await websocket.close(code=1011)

@router.websocket("/ws/notifications")
async def websocket_notifications(
    websocket: WebSocket,
    user_id: str = None
):
    """WebSocket for notifications (demo - no auth for simplicity)"""
    await websocket.accept()
    
    try:
        # Simulate sending notifications
        await websocket.send_json({
            "type": "welcome",
            "message": "Connected to notification service",
            "timestamp": datetime.utcnow().isoformat()
        })
        
        # Send a demo notification after 5 seconds
        await asyncio.sleep(5)
        await websocket.send_json({
            "type": "notification",
            "title": "📚 Reading Reminder",
            "message": "Don't forget to read today to keep your streak alive!",
            "category": "reminder",
            "timestamp": datetime.utcnow().isoformat()
        })
        
        while True:
            # Keep connection alive
            await websocket.receive_text()
            
    except WebSocketDisconnect:
        logger.info("Notification WebSocket disconnected")

# Utility function for WebSocket auth
async def get_current_user_ws(token: str):
    """Get user from WebSocket token (simplified)"""
    # In real app, decode JWT token
    # For demo, return a mock user
    from app.database import SessionLocal
    db = SessionLocal()
    try:
        # Simple token validation
        if token.startswith("user_"):
            user_id = token.replace("user_", "")
            user = db.query(models.User).filter(models.User.id == user_id).first()
            return user
        return None
    finally:
        db.close()