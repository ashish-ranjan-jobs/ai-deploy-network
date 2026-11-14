from typing import List

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from src.database import get_db
from src.models.user import User
from src.routers.deps import get_current_user
from src.schemas.deployment import DeploymentCreate, DeploymentOut, DeploymentUpdate
from src.services.deployment_service import (
    create_deployment,
    delete_deployment,
    get_deployment_by_id,
    list_user_deployments,
    list_verified_deployments,
    update_deployment,
)
from src.services.pdf_service import generate_deployment_pdf

router = APIRouter(prefix="/api/deployments", tags=["Deployments"])


@router.post("/", response_model=DeploymentOut, status_code=status.HTTP_201_CREATED)
def add_deployment(
    data: DeploymentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Add a genuine AI deployment case study and submit for verification."""
    deployment = create_deployment(db, user_id=current_user.id, data=data)
    return DeploymentOut.model_validate(deployment)


@router.get("/", response_model=List[DeploymentOut])
def get_verified_deployments(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
):
    """List public verified deployments."""
    deployments = list_verified_deployments(db, skip=skip, limit=limit)
    return [DeploymentOut.model_validate(d) for d in deployments]


@router.get("/my", response_model=List[DeploymentOut])
def get_my_deployments(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List all deployments published by the authenticated builder."""
    deployments = list_user_deployments(db, user_id=current_user.id)
    return [DeploymentOut.model_validate(d) for d in deployments]


@router.get("/{deployment_id}", response_model=DeploymentOut)
def get_deployment(deployment_id: int, db: Session = Depends(get_db)):
    """Get single deployment case study details."""
    deployment = get_deployment_by_id(db, deployment_id=deployment_id)
    if not deployment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Deployment case study not found",
        )
    return DeploymentOut.model_validate(deployment)


@router.put("/{deployment_id}", response_model=DeploymentOut)
def edit_deployment(
    deployment_id: int,
    data: DeploymentUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update a deployment case study."""
    deployment = update_deployment(db, deployment_id=deployment_id, user_id=current_user.id, data=data)
    if not deployment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Deployment not found or not owned by you",
        )
    return DeploymentOut.model_validate(deployment)


@router.delete("/{deployment_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_deployment(
    deployment_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete a deployment case study."""
    success = delete_deployment(db, deployment_id=deployment_id, user_id=current_user.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Deployment not found or not owned by you",
        )
    return None


@router.get("/{deployment_id}/export-pdf")
def export_single_deployment_pdf(deployment_id: int, db: Session = Depends(get_db)):
    """Export a single case study as a downloadable PDF."""
    deployment = get_deployment_by_id(db, deployment_id=deployment_id)
    if not deployment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Deployment not found",
        )

    pdf_bytes = generate_deployment_pdf(deployment)
    filename = f"case_study_{deployment.title[:30]}_{deployment.id}.pdf".replace(" ", "_")
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
