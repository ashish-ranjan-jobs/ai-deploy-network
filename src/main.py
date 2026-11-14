from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from src.config import get_settings
from src.database import Base, SessionLocal, engine
from src.models.membership import Membership
from src.models.user import User
from src.routers import (
    admin_router,
    auth_router,
    builders_router,
    deployments_router,
    search_router,
    web_router,
)
from src.services.auth_service import hash_password

settings = get_settings()


def init_db_and_seed():
    """Verify relational tables and ensure root admin exists."""
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        admin = db.query(User).filter(User.email == settings.ADMIN_EMAIL.lower()).first()
        if not admin:
            admin_user = User(
                first_name="Admin",
                last_name="Network",
                email=settings.ADMIN_EMAIL.lower(),
                password_hash=hash_password(settings.ADMIN_PASSWORD),
                title="Lead Registry Curator",
                company="AI Deploy Network",
                bio="Technical verifier for production architectures.",
                is_verified=True,
                is_admin=True,
            )
            db.add(admin_user)
            db.commit()
            db.refresh(admin_user)

            # Assign Founding Builder #001
            membership = Membership(
                user_id=admin_user.id,
                membership_number=1,
                tier="Founding Builder",
                badge_label="Founding Builder #001",
                is_active=True,
            )
            db.add(membership)
            db.commit()
    finally:
        db.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db_and_seed()
    yield


app = FastAPI(
    title=settings.APP_NAME,
    description="Independent Peer Registry of Validated AI Implementations.",
    version="1.1.0",
    docs_url="/aideploy/docs",
    redoc_url="/aideploy/redoc",
    openapi_url="/aideploy/openapi.json",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files mounted under /aideploy/static
static_dir = Path(__file__).resolve().parent / "static"
static_dir.mkdir(parents=True, exist_ok=True)
app.mount("/aideploy/static", StaticFiles(directory=str(static_dir)), name="aideploy-static")

# Mount Routers
app.include_router(web_router)
app.include_router(auth_router, prefix="/aideploy")
app.include_router(builders_router, prefix="/aideploy")
app.include_router(deployments_router, prefix="/aideploy")
app.include_router(search_router, prefix="/aideploy")
app.include_router(admin_router, prefix="/aideploy")

# Also include un-prefixed routers so unit tests and direct calls work
app.include_router(auth_router)
app.include_router(builders_router)
app.include_router(deployments_router)
app.include_router(search_router)
app.include_router(admin_router)


@app.get("/aideploy/api/health", tags=["Health"])
@app.get("/api/health", tags=["Health"])
def health_check():
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "environment": settings.APP_ENV,
        "base_path": settings.BASE_PATH,
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("src.main:app", host="0.0.0.0", port=settings.APP_PORT, reload=True)
