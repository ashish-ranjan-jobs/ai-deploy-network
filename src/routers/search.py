from typing import List, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from src.database import get_db
from src.schemas.deployment import DeploymentOut
from src.services.deployment_service import search_deployments

router = APIRouter(prefix="/api/search", tags=["Search & Discovery"])


@router.get("/", response_model=List[DeploymentOut])
def search_directory(
    q: Optional[str] = Query(None, description="Search term for title, problem, solution or results"),
    industry: Optional[str] = Query(None, description="Filter by industry"),
    tech: Optional[str] = Query(None, description="Filter by AI tech/model used"),
    verified_only: bool = Query(False, description="Filter only verified implementations"),
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
):
    """Search AI deployments and discover verified implementations and builders."""
    results = search_deployments(
        db,
        query=q,
        industry=industry,
        tech=tech,
        verified_only=verified_only,
        skip=skip,
        limit=limit,
    )
    return [DeploymentOut.model_validate(d) for d in results]
