from fastapi.testclient import TestClient

from src.models.user import User


def test_landing_page_renders(client: TestClient):
    response = client.get("/")
    assert response.status_code == 200
    assert "AI Deploy Network" in response.text
    assert "Founding Builder" in response.text


def test_register_page_renders(client: TestClient):
    response = client.get("/register")
    assert response.status_code == 200
    assert "Claim Your Builder Profile" in response.text


def test_login_page_renders(client: TestClient):
    response = client.get("/login")
    assert response.status_code == 200
    assert "Sign In to Your Profile" in response.text


def test_search_page_renders(client: TestClient):
    response = client.get("/search")
    assert response.status_code == 200
    assert "AI Implementation Directory" in response.text


def test_public_profile_renders(client: TestClient, test_user: User):
    response = client.get(f"/profile/{test_user.id}")
    assert response.status_code == 200
    assert test_user.first_name in response.text
    assert "Documented AI Deployments" in response.text
