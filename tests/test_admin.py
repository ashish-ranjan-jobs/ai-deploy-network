from fastapi.testclient import TestClient


def test_admin_permissions_required(client: TestClient, auth_headers: dict[str, str]):
    # Regular user attempting admin route
    res = client.get("/api/admin/pending", headers=auth_headers)
    assert res.status_code == 403


def test_admin_verify_and_approve_deployment(
    client: TestClient,
    auth_headers: dict[str, str],
    admin_auth_headers: dict[str, str],
):
    # User creates deployment
    payload = {
        "title": "LLM Customer Support Agent for Telecom",
        "industry": "Telecom",
        "ai_tech_used": "Llama 3, vLLM, LangGraph",
        "problem_statement": "High inbound volume with 18m wait times.",
        "solution_description": "Multi-agent LangGraph workflow running on self-hosted vLLM cluster.",
        "measurable_results": "Handled 65% of Tier-1 queries autonomously, customer satisfaction up by 28%.",
    }
    dep = client.post("/api/deployments/", json=payload, headers=auth_headers).json()
    dep_id = dep["id"]

    # Admin checks pending queue
    pending_res = client.get("/api/admin/pending", headers=admin_auth_headers)
    assert pending_res.status_code == 200
    pending_list = pending_res.json()
    assert any(d["id"] == dep_id for d in pending_list)

    # Admin approves submission
    review_payload = {
        "status": "APPROVED",
        "feedback_notes": "Verified genuine production metrics and multi-agent setup.",
    }
    verify_res = client.post(
        f"/api/admin/verify/{dep_id}",
        json=review_payload,
        headers=admin_auth_headers,
    )
    assert verify_res.status_code == 200
    assert verify_res.json()["is_verified"] is True
    assert verify_res.json()["verification_status"] == "APPROVED"

    # Verify public listing reflects verified status
    verified_list = client.get("/api/deployments/").json()
    assert any(d["id"] == dep_id for d in verified_list)
