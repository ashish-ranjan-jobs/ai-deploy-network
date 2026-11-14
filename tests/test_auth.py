from fastapi.testclient import TestClient


def test_health_check(client: TestClient):
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_register_builder_success(client: TestClient):
    payload = {
        "first_name": "Alan",
        "last_name": "Turing",
        "email": "alan.turing@example.com",
        "password": "SecurePassword123!",
        "title": "Machine Intelligence Pioneer",
        "company": "Bletchley AI",
        "location": "Cambridge, UK",
        "linkedin_url": "https://linkedin.com/in/alanturing",
        "github_url": "https://github.com/aturing",
        "bio": "Foundations of modern AI and computing.",
    }
    response = client.post("/api/auth/register", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["email"] == "alan.turing@example.com"
    assert data["user"]["membership"] is not None
    assert "Founding Builder" in data["user"]["membership"]["tier"]


def test_register_duplicate_email_fails(client: TestClient):
    payload = {
        "first_name": "Claude",
        "last_name": "Shannon",
        "email": "claude@example.com",
        "password": "Password123!",
    }
    r1 = client.post("/api/auth/register", json=payload)
    assert r1.status_code == 201

    r2 = client.post("/api/auth/register", json=payload)
    assert r2.status_code == 400
    assert "already registered" in r2.json()["detail"]


def test_login_success_and_failure(client: TestClient):
    payload = {
        "first_name": "Geoffrey",
        "last_name": "Hinton",
        "email": "geoff@example.com",
        "password": "DeepLearning2026!",
    }
    client.post("/api/auth/register", json=payload)

    # Valid login
    login_res = client.post(
        "/api/auth/login",
        json={"email": "geoff@example.com", "password": "DeepLearning2026!"},
    )
    assert login_res.status_code == 200
    token_data = login_res.json()
    assert "access_token" in token_data

    # Invalid password
    bad_login = client.post(
        "/api/auth/login",
        json={"email": "geoff@example.com", "password": "WrongPassword"},
    )
    assert bad_login.status_code == 401


def test_get_current_user_me(client: TestClient, auth_headers: dict[str, str]):
    response = client.get("/api/auth/me", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "ada@example.com"
    assert data["first_name"] == "Ada"
    assert data["membership"]["membership_number"] == 2
