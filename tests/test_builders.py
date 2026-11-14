from fastapi.testclient import TestClient

from src.models.user import User


def test_get_slots_status(client: TestClient):
    response = client.get("/api/builders/slots")
    assert response.status_code == 200
    data = response.json()
    assert "slots_remaining" in data
    assert "total_granted" in data
    assert data["max_slots"] == 500


def test_get_builder_profile(client: TestClient, test_user: User):
    response = client.get(f"/api/builders/{test_user.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == test_user.id
    assert data["first_name"] == "Ada"
    assert data["membership"]["badge_label"] == "Founding Builder #002"


def test_update_builder_profile(client: TestClient, auth_headers: dict[str, str]):
    update_data = {
        "title": "Principal AI Architect",
        "bio": "Updated biography covering LLM production deployments.",
    }
    response = client.put("/api/builders/me", json=update_data, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Principal AI Architect"
    assert data["bio"] == "Updated biography covering LLM production deployments."


def test_export_builder_pdf(client: TestClient, test_user: User):
    response = client.get(f"/api/builders/{test_user.id}/export-pdf")
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    assert response.content.startswith(b"%PDF-")
