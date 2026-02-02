"""
API Module for Bibleo Library System
Contains all API endpoints organized by functionality
"""

from fastapi import APIRouter

# Import routers
from app.api.endpoints import router as api_router
from app.api.websocket import router as websocket_router

# Create main router
main_router = APIRouter()

# Include all routers
main_router.include_router(api_router, prefix="/api", tags=["API"])
main_router.include_router(websocket_router, prefix="/ws", tags=["WebSocket"])

# API Metadata
API_VERSION = "v1"
API_TITLE = "Bibleo Library Management API"
API_DESCRIPTION = """
# Bibleo AI Library Management System API

## Features

### 📚 Book Management
- Search books with AI-powered semantic search
- Get personalized recommendations
- Manage borrowing and returns

### 👤 User Management  
- User registration and authentication
- Reading progress tracking
- Streak maintenance

### 🤖 AI Features
- Intelligent book recommendations
- Semantic understanding search
- Demand prediction for inventory

### 📊 Analytics
- Reading statistics
- Library analytics
- User engagement metrics

### 🔔 Real-time Features
- WebSocket for live updates
- WhatsApp notifications
- Streak tracking

## Authentication
Most endpoints require JWT token authentication.
Use `/auth/login` to get your token.

## WebSocket
Connect to `/ws/streak` for real-time streak updates.
"""

# Export
__all__ = [
    "main_router",
    "api_router",
    "websocket_router",
    "API_VERSION",
    "API_TITLE",
    "API_DESCRIPTION"
]