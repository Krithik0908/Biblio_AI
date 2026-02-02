from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.openapi.docs import get_swagger_ui_html, get_redoc_html
from fastapi.openapi.utils import get_openapi
from contextlib import asynccontextmanager
import uvicorn
from typing import List, Dict
import logging
import os
from datetime import datetime

from app.database import engine, Base, SessionLocal
from app import models, schemas, crud
from app.auth import router as auth_router
from app.api import main_router, API_INFO
from app.ai import initialize_all_models
import asyncio

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Startup time for health check
STARTUP_TIME = datetime.utcnow()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup/shutdown events"""
    logger.info("🚀 Starting Bibleo AI Library System...")
    
    # Create database tables
    logger.info("🗄️ Creating database tables...")
    Base.metadata.create_all(bind=engine)
    
    # Load initial data
    logger.info("📊 Loading initial data...")
    await load_initial_data()
    
    # Initialize AI models asynchronously
    logger.info("🤖 Initializing AI models...")
    await initialize_all_models()
    
    logger.info("✅ Bibleo backend is ready!")
    
    yield
    
    logger.info("👋 Shutting down Bibleo backend...")

# Create FastAPI app with metadata
app = FastAPI(
    title=API_INFO["title"],
    description=API_INFO["description"],
    version=API_INFO["version"],
    contact=API_INFO["contact"],
    license_info=API_INFO["license"],
    docs_url=None,  # We'll customize docs
    redoc_url=None,  # We'll customize redoc
    lifespan=lifespan
)

# Custom OpenAPI schema
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    
    # Customize schema
    openapi_schema["info"]["x-logo"] = {
        "url": "https://fastapi.tiangolo.com/img/logo-margin/logo-teal.png",
        "altText": "Bibleo Logo"
    }
    
    # Add security schemes
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": "Enter JWT token in format: Bearer <token>"
        }
    }
    
    # Secure all endpoints by default
    for path in openapi_schema["paths"].values():
        for method in path.values():
            method.setdefault("security", [{"BearerAuth": []}])
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Include routers
app.include_router(auth_router, prefix="/auth", tags=["Authentication"])
app.include_router(main_router)

# Custom docs endpoints
@app.get("/docs", include_in_schema=False)
async def custom_docs():
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=app.title + " - Swagger UI",
        swagger_favicon_url="/static/favicon.ico",
        swagger_js_url="/static/swagger-ui-bundle.js",
        swagger_css_url="/static/swagger-ui.css",
    )

@app.get("/redoc", include_in_schema=False)
async def custom_redoc():
    return get_redoc_html(
        openapi_url=app.openapi_url,
        title=app.title + " - ReDoc",
        redoc_favicon_url="/static/favicon.ico",
        redoc_js_url="/static/redoc.standalone.js",
    )

# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    return {
        "message": "Welcome to Bibleo AI Library Management System",
        "version": app.version,
        "team": "SignalX Collective",
        "docs": "/docs",
        "redoc": "/redoc",
        "endpoints": {
            "auth": "/auth",
            "api": "/api",
            "websocket": "/ws",
            "health": "/health"
        }
    }

# Health check endpoint
@app.get("/health", response_model=schemas.HealthCheck, tags=["Health"])
async def health_check():
    """Health check endpoint for monitoring"""
    from app.ai import are_models_initialized
    
    # Check database connection
    db_healthy = False
    try:
        db = SessionLocal()
        db.execute("SELECT 1")
        db_healthy = True
        db.close()
    except Exception:
        pass
    
    # Calculate uptime
    uptime = (datetime.utcnow() - STARTUP_TIME).total_seconds()
    
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow(),
        "service": "bibleo-backend",
        "database": db_healthy,
        "ai_models": are_models_initialized(),
        "uptime": round(uptime, 2)
    }

# System info endpoint
@app.get("/system/info", tags=["System"])
async def system_info():
    """Get system information"""
    import platform
    import psutil
    
    return {
        "system": {
            "platform": platform.platform(),
            "python_version": platform.python_version(),
            "cpu_count": psutil.cpu_count(),
            "memory_total": psutil.virtual_memory().total,
            "memory_available": psutil.virtual_memory().available,
        },
        "app": {
            "version": app.version,
            "startup_time": STARTUP_TIME.isoformat(),
            "environment": os.getenv("ENVIRONMENT", "development"),
        }
    }

async def load_initial_data():
    """Load initial sample data"""
    db = SessionLocal()
    try:
        # Check if we need to load sample books
        book_count = db.query(models.Book).count()
        user_count = db.query(models.User).count()
        
        if book_count == 0:
            logger.info("📚 Loading sample books...")
            sample_books = [
                models.Book(
                    title="The Alchemist",
                    author="Paulo Coelho",
                    isbn="9780062315007",
                    genre=models.Genre.FICTION,
                    sub_genre="Inspirational",
                    description="A fable about following your dreams",
                    summary="A shepherd boy's journey to find his personal legend",
                    pages=208,
                    total_copies=10,
                    available_copies=8,
                    views=1500,
                    rating=4.5,
                    tags=["inspiration", "dreams", "adventure"],
                    difficulty_level="beginner"
                ),
                models.Book(
                    title="Atomic Habits",
                    author="James Clear",
                    isbn="9780735211292",
                    genre=models.Genre.SELF_HELP,
                    sub_genre="Productivity",
                    description="Build good habits and break bad ones",
                    summary="A guide to building good habits through tiny changes",
                    pages=320,
                    total_copies=15,
                    available_copies=12,
                    views=2300,
                    rating=4.7,
                    tags=["habits", "productivity", "self-improvement"],
                    difficulty_level="intermediate"
                ),
                models.Book(
                    title="The Silent Patient",
                    author="Alex Michaelides",
                    isbn="9781250301703",
                    genre=models.Genre.HORROR,
                    sub_genre="Psychological Thriller",
                    description="A psychological thriller about a woman who shoots her husband",
                    summary="A famous painter stops speaking after shooting her husband",
                    pages=336,
                    total_copies=8,
                    available_copies=5,
                    views=1800,
                    rating=4.2,
                    tags=["thriller", "mystery", "psychological"],
                    difficulty_level="intermediate"
                ),
            ]
            db.add_all(sample_books)
            db.commit()
            logger.info(f"✅ Loaded {len(sample_books)} sample books")
        
        if user_count == 0:
            logger.info("👤 Creating sample admin user...")
            # Create admin user (password: admin123)
            from app.auth import get_password_hash
            admin_user = models.User(
                name="Admin User",
                email="admin@bibleo.com",
                password_hash=get_password_hash("admin123"),
                role=models.UserRole.ADMIN,
                age_group=models.AgeGroup.ADULT,
                is_verified=True
            )
            db.add(admin_user)
            db.commit()
            logger.info("✅ Created admin user (admin@bibleo.com / admin123)")
            
    except Exception as e:
        logger.error(f"❌ Error loading initial data: {e}")
        db.rollback()
    finally:
        db.close()

# Main entry point
if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        reload=os.getenv("ENVIRONMENT") == "development",
        log_level="info",
        access_log=True
    )