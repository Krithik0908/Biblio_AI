"""
Bibleo AI Library Management System - Backend
SignalX Collective | iCUBE 5.0

A complete AI-driven library management system with:
- FastAPI backend
- PostgreSQL database
- AI-powered recommendations
- Semantic search
- Real-time updates
- WhatsApp notifications
"""

__version__ = "5.0.0"
__author__ = "SignalX Collective"
__description__ = "AI-Driven Library Management System"
__license__ = "MIT"
__email__ = "team@signalxcollective.com"
__website__ = "https://github.com/signalxcollective/bibleo"

# Export main components
__all__ = [
    # Main app
    "app",
    
    # Models
    "User",
    "Book",
    "Borrowing",
    "ReadingSession",
    "Review",
    
    # Schemas
    "UserResponse",
    "BookResponse",
    "Token",
    
    # AI
    "RecommendationEngine",
    "SemanticSearch",
    "DemandPredictor",
    
    # API
    "main_router",
    "api_router",
    "websocket_router"
]

# Version info for API
API_INFO = {
    "version": __version__,
    "title": "Bibleo API",
    "description": __description__,
    "contact": {
        "name": __author__,
        "email": __email__,
        "url": __website__
    },
    "license": {
        "name": __license__,
        "url": "https://opensource.org/licenses/MIT"
    }
}