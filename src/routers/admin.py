from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from src.database import get_db
from src.models.deployment import Deployment
from src.models.membership import Membership
from src.models.user import User
from src.routers.deps import get_current_admin
from src.schemas.deployment import DeploymentOut
from src.schemas.verification import VerificationReview
from src.services.deployment_service import review_deployment

router = APIRouter(prefix="/api/admin", tags=["Admin Verification"])


@router.get("/pending", response_model=List[DeploymentOut])
def get_pending_deployments(
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_current_admin),
):
    """List deployments awaiting verification review."""
    pending = (
        db.query(Deployment)
        .filter(Deployment.verification_status == "PENDING")
        .order_by(Deployment.created_at.asc())
        .all()
    )
    return [DeploymentOut.model_validate(p) for p in pending]


@router.post("/verify/{deployment_id}", response_model=DeploymentOut)
def verify_deployment(
    deployment_id: int,
    review_data: VerificationReview,
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_current_admin),
):
    """Review and verify or reject an AI deployment submission."""
    deployment = review_deployment(
        db,
        deployment_id=deployment_id,
        reviewer_id=admin_user.id,
        review_data=review_data,
    )
    if not deployment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Deployment not found",
        )
    return DeploymentOut.model_validate(deployment)


@router.get("/stats")
def get_admin_stats(
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_current_admin),
):
    """Get high-level platform metrics for administration."""
    total_users = db.query(func.count(User.id)).scalar() or 0
    total_deployments = db.query(func.count(Deployment.id)).scalar() or 0
    verified_deployments = db.query(func.count(Deployment.id)).filter(Deployment.is_verified.is_(True)).scalar() or 0
    pending_deployments = (
        db.query(func.count(Deployment.id)).filter(Deployment.verification_status == "PENDING").scalar() or 0
    )
    total_founding_members = (
        db.query(func.count(Membership.id)).filter(Membership.tier == "Founding Builder").scalar() or 0
    )

    return {
        "total_users": total_users,
        "total_deployments": total_deployments,
        "verified_deployments": verified_deployments,
        "pending_deployments": pending_deployments,
        "total_founding_members": total_founding_members,
    }
