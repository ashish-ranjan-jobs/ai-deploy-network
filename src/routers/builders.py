from typing import List

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from src.database import get_db
from src.models.user import User
from src.routers.deps import get_current_user
from src.schemas.membership import MembershipStats
from src.schemas.user import UserOut, UserUpdate
from src.services.builder_service import get_user_by_id, list_builders, update_builder_profile
from src.services.deployment_service import list_user_deployments
from src.services.membership_service import get_membership_stats
from src.services.pdf_service import generate_builder_profile_pdf

router = APIRouter(prefix="/api/builders", tags=["Builders"])


@router.get("/slots", response_model=MembershipStats)
def get_slots_status(db: Session = Depends(get_db)):
    """Return count of claimed and remaining Founding Builder spots."""
    return get_membership_stats(db)


@router.get("/", response_model=List[UserOut])
def get_builders(
    skip: int = 0,
    limit: int = 50,
    verified_only: bool = False,
    db: Session = Depends(get_db),
):
    """List builders in the directory."""
    builders = list_builders(db, skip=skip, limit=limit, verified_only=verified_only)
    return [UserOut.model_validate(b) for b in builders]


@router.get("/me", response_model=UserOut)
def get_my_profile(current_user: User = Depends(get_current_user)):
    """Get authenticated user profile."""
    return UserOut.model_validate(current_user)


@router.put("/me", response_model=UserOut)
def update_my_profile(
    data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update profile information for the authenticated builder."""
    updated = update_builder_profile(db, current_user.id, data)
    if not updated:
        raise HTTPException(status_code=404, detail="User not found")
    return UserOut.model_validate(updated)


@router.get("/{user_id}", response_model=UserOut)
def get_builder_by_id(user_id: int, db: Session = Depends(get_db)):
    """Retrieve public builder profile by user ID."""
    user = get_user_by_id(db, user_id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Builder not found",
        )
    return UserOut.model_validate(user)


@router.get("/{user_id}/export-pdf")
def export_builder_pdf(user_id: int, db: Session = Depends(get_db)):
    """Download verified builder profile and case studies as a PDF portfolio."""
    user = get_user_by_id(db, user_id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Builder not found",
        )

    deployments = list_user_deployments(db, user_id=user.id)
    pdf_bytes = generate_builder_profile_pdf(user, deployments)

    filename = f"builder_{user.first_name}_{user.last_name}_portfolio.pdf".replace(" ", "_")
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
