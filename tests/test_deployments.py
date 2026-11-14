from fastapi.testclient import TestClient


def test_create_and_get_deployment(client: TestClient, auth_headers: dict[str, str]):
    payload = {
        "title": "Autonomous Financial Document Processing RAG System",
        "client_or_company": "Global Asset Management Corp",
        "industry": "FinTech",
        "ai_tech_used": "Claude 3.5 Sonnet, pgvector, LangChain, FastAPI",
        "deployment_stage": "Production",
        "problem_statement": "Manual auditing of investment memos was taking 45 minutes per memo across 10,000 files.",
        "solution_description": "Architected a hybrid vector-BM25 retrieval engine with semantic chunking and automated citation extraction.",
        "measurable_results": "Reduced review cycle from 45 minutes to 35 seconds per document. 99.8% precision rate. Saved $480k annually.",
        "live_demo_url": "https://rag.example.com",
        "repo_url": "https://github.com/example/rag-pipeline",
    }
    create_res = client.post("/api/deployments/", json=payload, headers=auth_headers)
    assert create_res.status_code == 201
    dep_data = create_res.json()
    assert dep_data["title"] == payload["title"]
    assert dep_data["verification_status"] == "PENDING"
    assert dep_data["is_verified"] is False
    dep_id = dep_data["id"]

    # Get single deployment
    get_res = client.get(f"/api/deployments/{dep_id}")
    assert get_res.status_code == 200
    assert get_res.json()["id"] == dep_id

    # List my deployments
    my_res = client.get("/api/deployments/my", headers=auth_headers)
    assert my_res.status_code == 200
    assert len(my_res.json()) >= 1

    # Export PDF case study
    pdf_res = client.get(f"/api/deployments/{dep_id}/export-pdf")
    assert pdf_res.status_code == 200
    assert pdf_res.headers["content-type"] == "application/pdf"
    assert pdf_res.content.startswith(b"%PDF-")


def test_update_and_delete_deployment(client: TestClient, auth_headers: dict[str, str]):
    payload = {
        "title": "Initial Title",
        "industry": "Healthcare",
        "ai_tech_used": "PyTorch, ResNet-50",
        "problem_statement": "Medical image triage latency bottleneck.",
        "solution_description": "Fine-tuned computer vision classifier deployed on Triton Inference Server.",
        "measurable_results": "Triaged 200,000 scans with 98.4% sensitivity.",
    }
    dep = client.post("/api/deployments/", json=payload, headers=auth_headers).json()
    dep_id = dep["id"]

    # Update
    update_res = client.put(
        f"/api/deployments/{dep_id}",
        json={"title": "Updated Title for Radiology Classifier"},
        headers=auth_headers,
    )
    assert update_res.status_code == 200
    assert update_res.json()["title"] == "Updated Title for Radiology Classifier"

    # Delete
    del_res = client.delete(f"/api/deployments/{dep_id}", headers=auth_headers)
    assert del_res.status_code == 204

    # Verify deleted
    get_deleted = client.get(f"/api/deployments/{dep_id}")
    assert get_deleted.status_code == 404
