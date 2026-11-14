from fastapi.testclient import TestClient

from src.models.user import User


def test_landing_page_renders(client: TestClient):
    response = client.get("/aideploy/")
    assert response.status_code == 200
    assert "AI Deploy Network" in response.text
    assert "FOUNDING REGISTRY" in response.text


def test_register_page_renders(client: TestClient):
    response = client.get("/aideploy/register")
    assert response.status_code == 200
    assert "Claim Builder Allocation" in response.text


def test_login_page_renders(client: TestClient):
    response = client.get("/aideploy/login")
    assert response.status_code == 200
    assert "Builder Sign In" in response.text


def test_search_page_renders(client: TestClient):
    response = client.get("/aideploy/search")
    assert response.status_code == 200
    assert "AI Implementation Directory" in response.text


def test_public_profile_renders(client: TestClient, test_user: User):
    response = client.get(f"/aideploy/profile/{test_user.id}")
    assert response.status_code == 200
    assert test_user.first_name in response.text
    assert "DOCUMENTED_DEPLOYMENTS" in response.text
