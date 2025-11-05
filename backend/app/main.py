"""
FastAPI Main Application
Entry point for the backend API service
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os
from dotenv import load_dotenv
from app.config import settings
from app.database import init_db
from app.api.auth import router as auth_router
from app.api.users import router as users_router
from app.api.gmail import router as gmail_router
from app.api.watch import router as watch_router
from app.api.ai import router as ai_router
from app.api.project import router as project_router
from app.api.processing import router as processing_router

# Load environment variables
load_dotenv()

# Lifespan context manager for startup/shutdown events
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("🚀 Starting AI Email Extension Backend...")
    print(f"📊 Initializing database...")
    init_db()
    print("✅ Database initialized")
    yield
    # Shutdown
    print("🛑 Shutting down backend...")

# Create FastAPI application
app = FastAPI(
    title="AI Email Extension API",
    description="Backend API for AI-powered Gmail email grouping extension",
    version="0.1.0",
    lifespan=lifespan
)

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(auth_router)
app.include_router(users_router)
app.include_router(gmail_router)
app.include_router(watch_router)
app.include_router(ai_router)
app.include_router(project_router)
app.include_router(processing_router)

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "AI Email Extension API",
        "version": "0.1.0"
    }

@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "service": "AI Email Extension API",
        "version": "0.1.0",
        "environment": settings.environment
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=os.getenv("BACKEND_HOST", "localhost"),
        port=int(os.getenv("BACKEND_PORT", 8000)),
        reload=os.getenv("DEBUG", "False").lower() == "true"
    )

