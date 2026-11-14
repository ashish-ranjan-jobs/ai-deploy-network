from datetime import datetime, timezone
from typing import List, Optional

from sqlalchemy import or_
from sqlalchemy.orm import Session, joinedload

from src.models.deployment import Deployment
from src.models.user import User
from src.models.verification import Verification
from src.schemas.deployment import DeploymentCreate, DeploymentUpdate
from src.schemas.verification import VerificationReview


def create_deployment(db: Session, user_id: int, data: DeploymentCreate) -> Deployment:
    deployment = Deployment(
        user_id=user_id,
        title=data.title,
        client_or_company=data.client_or_company,
        industry=data.industry,
        ai_tech_used=data.ai_tech_used,
        deployment_stage=data.deployment_stage,
        hardware_target=data.hardware_target or "Cloud (GPU/vLLM)",
        problem_statement=data.problem_statement,
        solution_description=data.solution_description,
        measurable_results=data.measurable_results,
        live_demo_url=data.live_demo_url,
        repo_url=data.repo_url,
        is_verified=False,
        verification_status="PENDING",
    )
    db.add(deployment)
    db.commit()
    db.refresh(deployment)

    verif = Verification(
        deployment_id=deployment.id,
        status="PENDING",
    )
    db.add(verif)
    db.commit()
    db.refresh(deployment)
    return deployment


def get_deployment_by_id(db: Session, deployment_id: int) -> Optional[Deployment]:
    return (
        db.query(Deployment)
        .options(joinedload(Deployment.user).joinedload(User.membership))
        .filter(Deployment.id == deployment_id)
        .first()
    )


def list_user_deployments(db: Session, user_id: int) -> List[Deployment]:
    return db.query(Deployment).filter(Deployment.user_id == user_id).order_by(Deployment.created_at.desc()).all()


def list_verified_deployments(db: Session, skip: int = 0, limit: int = 50) -> List[Deployment]:
    return (
        db.query(Deployment)
        .options(joinedload(Deployment.user).joinedload(User.membership))
        .filter(Deployment.is_verified.is_(True))
        .order_by(Deployment.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def search_deployments(
    db: Session,
    query: Optional[str] = None,
    industry: Optional[str] = None,
    tech: Optional[str] = None,
    verified_only: bool = False,
    skip: int = 0,
    limit: int = 50,
) -> List[Deployment]:
    q = db.query(Deployment).options(joinedload(Deployment.user).joinedload(User.membership))

    if verified_only:
        q = q.filter(Deployment.is_verified.is_(True))

    if query:
        pattern = f"%{query}%"
        q = q.filter(
            or_(
                Deployment.title.ilike(pattern),
                Deployment.problem_statement.ilike(pattern),
                Deployment.solution_description.ilike(pattern),
                Deployment.measurable_results.ilike(pattern),
                Deployment.ai_tech_used.ilike(pattern),
            )
        )

    if industry:
        q = q.filter(Deployment.industry.ilike(f"%{industry}%"))

    if tech:
        q = q.filter(Deployment.ai_tech_used.ilike(f"%{tech}%"))

    return q.order_by(Deployment.created_at.desc()).offset(skip).limit(limit).all()


def update_deployment(
    db: Session,
    deployment_id: int,
    user_id: int,
    data: DeploymentUpdate,
) -> Optional[Deployment]:
    deployment = db.query(Deployment).filter(Deployment.id == deployment_id, Deployment.user_id == user_id).first()
    if not deployment:
        return None

    update_dict = data.model_dump(exclude_unset=True)
    for key, value in update_dict.items():
        setattr(deployment, key, value)

    deployment.is_verified = False
    deployment.verification_status = "PENDING"
    deployment.updated_at = datetime.now(timezone.utc)

    verif = Verification(
        deployment_id=deployment.id,
        status="PENDING",
        feedback_notes="Spec updated; queued for re-verification.",
    )
    db.add(verif)
    db.commit()
    db.refresh(deployment)
    return deployment


def delete_deployment(db: Session, deployment_id: int, user_id: int) -> bool:
    deployment = db.query(Deployment).filter(Deployment.id == deployment_id, Deployment.user_id == user_id).first()
    if not deployment:
        return False
    db.delete(deployment)
    db.commit()
    return True


def review_deployment(
    db: Session,
    deployment_id: int,
    reviewer_id: int,
    review_data: VerificationReview,
) -> Optional[Deployment]:
    deployment = db.query(Deployment).filter(Deployment.id == deployment_id).first()
    if not deployment:
        return None

    is_approved = review_data.status == "APPROVED"
    deployment.is_verified = is_approved
    deployment.verification_status = review_data.status
    deployment.updated_at = datetime.now(timezone.utc)
    if is_approved:
        deployment.verification_hash = deployment.compute_audit_hash()

    user = db.query(User).filter(User.id == deployment.user_id).first()
    if user and is_approved:
        user.is_verified = True

    verif = Verification(
        deployment_id=deployment.id,
        reviewer_id=reviewer_id,
        status=review_data.status,
        feedback_notes=review_data.feedback_notes,
        reviewed_at=datetime.now(timezone.utc),
    )
    db.add(verif)
    db.commit()
    db.refresh(deployment)
    return deployment
