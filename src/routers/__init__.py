from src.routers.admin import router as admin_router
from src.routers.auth import router as auth_router
from src.routers.builders import router as builders_router
from src.routers.deployments import router as deployments_router
from src.routers.search import router as search_router
from src.routers.web import router as web_router

__all__ = [
    "auth_router",
    "builders_router",
    "deployments_router",
    "search_router",
    "admin_router",
    "web_router",
]
