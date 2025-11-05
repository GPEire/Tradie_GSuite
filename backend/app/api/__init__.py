"""
API Routes
"""

from app.api.auth import router as auth_router
from app.api.users import router as users_router
from app.api.gmail import router as gmail_router
from app.api.watch import router as watch_router
from app.api.ai import router as ai_router

__all__ = ["auth_router", "users_router", "gmail_router", "watch_router", "ai_router"]

