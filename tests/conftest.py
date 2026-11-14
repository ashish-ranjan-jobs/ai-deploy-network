from typing import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from src.database import Base, get_db
from src.main import app
from src.models.membership import Membership
from src.models.user import User
from src.services.auth_service import create_access_token, hash_password

# In-memory SQLite engine for tests
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session() -> Generator[Session, None, None]:
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session: Session) -> Generator[TestClient, None, None]:
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def test_user(db_session: Session) -> User:
    user = User(
        first_name="Ada",
        last_name="Lovelace",
        email="ada@example.com",
        password_hash=hash_password("Pass123!"),
        title="AI Research Lead",
        company="Algorithmic Systems",
        location="London, UK",
        is_verified=False,
        is_admin=False,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    membership = Membership(
        user_id=user.id,
        membership_number=2,
        tier="Founding Builder",
        badge_label="Founding Builder #002",
        is_active=True,
    )
    db_session.add(membership)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def auth_headers(test_user: User) -> dict[str, str]:
    token = create_access_token({"sub": str(test_user.id)})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def test_admin(db_session: Session) -> User:
    admin = User(
        first_name="Admin",
        last_name="Super",
        email="superadmin@example.com",
        password_hash=hash_password("AdminPass123!"),
        title="Chief Verifier",
        company="AI Deploy Network",
        is_verified=True,
        is_admin=True,
    )
    db_session.add(admin)
    db_session.commit()
    db_session.refresh(admin)

    membership = Membership(
        user_id=admin.id,
        membership_number=1,
        tier="Founding Builder",
        badge_label="Founding Builder #001",
        is_active=True,
    )
    db_session.add(membership)
    db_session.commit()
    db_session.refresh(admin)
    return admin


@pytest.fixture
def admin_auth_headers(test_admin: User) -> dict[str, str]:
    token = create_access_token({"sub": str(test_admin.id)})
    return {"Authorization": f"Bearer {token}"}
