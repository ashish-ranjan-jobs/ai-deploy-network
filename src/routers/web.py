from pathlib import Path
from typing import Optional

from fastapi import APIRouter, Depends, Form, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import func
from sqlalchemy.orm import Session

from src.database import get_db
from src.models.deployment import Deployment
from src.models.membership import Membership
from src.models.user import User
from src.routers.deps import get_current_user_optional
from src.schemas.deployment import DeploymentCreate, DeploymentUpdate
from src.schemas.user import UserRegister
from src.schemas.verification import VerificationReview
from src.services.auth_service import create_access_token
from src.services.builder_service import authenticate_user, get_user_by_id, list_builders, register_builder
from src.services.deployment_service import (
    create_deployment,
    delete_deployment,
    get_deployment_by_id,
    list_user_deployments,
    list_verified_deployments,
    review_deployment,
    search_deployments,
    update_deployment,
)
from src.services.membership_service import get_membership_stats

templates_dir = Path(__file__).resolve().parent.parent / "templates"
templates = Jinja2Templates(directory=str(templates_dir))

router = APIRouter(include_in_schema=False)


@router.get("/", response_class=HTMLResponse)
def home_page(
    request: Request,
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db),
):
    stats = get_membership_stats(db)
    featured = list_verified_deployments(db, limit=6)
    if not featured:
        featured = db.query(Deployment).order_by(Deployment.created_at.desc()).limit(6).all()
    total_deps = db.query(func.count(Deployment.id)).scalar() or 0

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "current_user": current_user,
            "stats": stats,
            "featured_deployments": featured,
            "total_deployments": total_deps,
        },
    )


@router.get("/register", response_class=HTMLResponse)
def register_page(
    request: Request,
    current_user: Optional[User] = Depends(get_current_user_optional),
):
    if current_user:
        return RedirectResponse(url="/dashboard", status_code=status.HTTP_303_SEE_OTHER)
    return templates.TemplateResponse(
        request=request,
        name="register.html",
        context={"current_user": None},
    )


@router.post("/register")
def handle_register(
    request: Request,
    first_name: str = Form(...),
    last_name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    title: Optional[str] = Form(None),
    company: Optional[str] = Form(None),
    location: Optional[str] = Form(None),
    linkedin_url: Optional[str] = Form(None),
    github_url: Optional[str] = Form(None),
    bio: Optional[str] = Form(None),
    db: Session = Depends(get_db),
):
    try:
        user_in = UserRegister(
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=password,
            title=title or None,
            company=company or None,
            location=location or None,
            linkedin_url=linkedin_url or None,
            github_url=github_url or None,
            bio=bio or None,
        )
        existing = db.query(User).filter(User.email == email.lower().strip()).first()
        if existing:
            return templates.TemplateResponse(
                request=request,
                name="register.html",
                context={"current_user": None, "error": "Email is already registered. Please sign in."},
                status_code=400,
            )

        user = register_builder(db, user_in)
        token = create_access_token({"sub": str(user.id)})
        resp = RedirectResponse(url="/dashboard", status_code=status.HTTP_303_SEE_OTHER)
        resp.set_cookie("access_token", f"Bearer {token}", httponly=True, samesite="lax", max_age=86400)
        return resp
    except Exception as e:
        return templates.TemplateResponse(
            request=request,
            name="register.html",
            context={"current_user": None, "error": str(e)},
            status_code=400,
        )


@router.get("/login", response_class=HTMLResponse)
def login_page(
    request: Request,
    current_user: Optional[User] = Depends(get_current_user_optional),
):
    if current_user:
        return RedirectResponse(url="/dashboard", status_code=status.HTTP_303_SEE_OTHER)
    return templates.TemplateResponse(
        request=request,
        name="login.html",
        context={"current_user": None},
    )


@router.post("/login")
def handle_login(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    user = authenticate_user(db, email, password)
    if not user:
        return templates.TemplateResponse(
            request=request,
            name="login.html",
            context={"current_user": None, "error": "Invalid email address or password."},
            status_code=401,
        )

    token = create_access_token({"sub": str(user.id)})
    resp = RedirectResponse(url="/dashboard", status_code=status.HTTP_303_SEE_OTHER)
    resp.set_cookie("access_token", f"Bearer {token}", httponly=True, samesite="lax", max_age=86400)
    return resp


@router.get("/dashboard", response_class=HTMLResponse)
def dashboard_page(
    request: Request,
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db),
):
    if not current_user:
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)

    deployments = list_user_deployments(db, current_user.id)
    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context={
            "current_user": current_user,
            "deployments": deployments,
        },
    )


@router.get("/profile/{user_id}", response_class=HTMLResponse)
def public_profile_page(
    user_id: int,
    request: Request,
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db),
):
    builder = get_user_by_id(db, user_id=user_id)
    if not builder:
        return RedirectResponse(url="/search", status_code=status.HTTP_303_SEE_OTHER)

    deployments = list_user_deployments(db, user_id=user_id)
    return templates.TemplateResponse(
        request=request,
        name="profile.html",
        context={
            "current_user": current_user,
            "builder": builder,
            "deployments": deployments,
        },
    )


@router.get("/deployments/new", response_class=HTMLResponse)
def new_deployment_page(
    request: Request,
    current_user: Optional[User] = Depends(get_current_user_optional),
):
    if not current_user:
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)
    return templates.TemplateResponse(
        request=request,
        name="deployment_form.html",
        context={"current_user": current_user, "deployment": None},
    )


@router.post("/deployments/new")
def handle_new_deployment(
    request: Request,
    title: str = Form(...),
    industry: str = Form(...),
    deployment_stage: str = Form(...),
    ai_tech_used: str = Form(...),
    problem_statement: str = Form(...),
    solution_description: str = Form(...),
    measurable_results: str = Form(...),
    client_or_company: Optional[str] = Form(None),
    live_demo_url: Optional[str] = Form(None),
    repo_url: Optional[str] = Form(None),
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db),
):
    if not current_user:
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)

    dep_in = DeploymentCreate(
        title=title,
        industry=industry,
        deployment_stage=deployment_stage,
        ai_tech_used=ai_tech_used,
        problem_statement=problem_statement,
        solution_description=solution_description,
        measurable_results=measurable_results,
        client_or_company=client_or_company or None,
        live_demo_url=live_demo_url or None,
        repo_url=repo_url or None,
    )
    create_deployment(db, current_user.id, dep_in)
    return RedirectResponse(url="/dashboard", status_code=status.HTTP_303_SEE_OTHER)


@router.get("/deployments/{deployment_id}/edit", response_class=HTMLResponse)
def edit_deployment_page(
    deployment_id: int,
    request: Request,
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db),
):
    if not current_user:
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)

    deployment = get_deployment_by_id(db, deployment_id)
    if not deployment or deployment.user_id != current_user.id:
        return RedirectResponse(url="/dashboard", status_code=status.HTTP_303_SEE_OTHER)

    return templates.TemplateResponse(
        request=request,
        name="deployment_form.html",
        context={"current_user": current_user, "deployment": deployment},
    )


@router.post("/deployments/{deployment_id}/edit")
def handle_edit_deployment(
    deployment_id: int,
    request: Request,
    title: str = Form(...),
    industry: str = Form(...),
    deployment_stage: str = Form(...),
    ai_tech_used: str = Form(...),
    problem_statement: str = Form(...),
    solution_description: str = Form(...),
    measurable_results: str = Form(...),
    client_or_company: Optional[str] = Form(None),
    live_demo_url: Optional[str] = Form(None),
    repo_url: Optional[str] = Form(None),
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db),
):
    if not current_user:
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)

    dep_update = DeploymentUpdate(
        title=title,
        industry=industry,
        deployment_stage=deployment_stage,
        ai_tech_used=ai_tech_used,
        problem_statement=problem_statement,
        solution_description=solution_description,
        measurable_results=measurable_results,
        client_or_company=client_or_company or None,
        live_demo_url=live_demo_url or None,
        repo_url=repo_url or None,
    )
    update_deployment(db, deployment_id, current_user.id, dep_update)
    return RedirectResponse(url="/dashboard", status_code=status.HTTP_303_SEE_OTHER)


@router.post("/deployments/{deployment_id}/delete")
def handle_delete_deployment(
    deployment_id: int,
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db),
):
    if current_user:
        delete_deployment(db, deployment_id, current_user.id)
    return RedirectResponse(url="/dashboard", status_code=status.HTTP_303_SEE_OTHER)


@router.get("/search", response_class=HTMLResponse)
def search_page(
    request: Request,
    q: Optional[str] = None,
    industry: Optional[str] = None,
    tech: Optional[str] = None,
    verified_only: Optional[str] = None,
    view: Optional[str] = "deployments",
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db),
):
    is_verified_only = verified_only in ["true", "1", "on"]
    deployments = search_deployments(
        db,
        query=q,
        industry=industry,
        tech=tech,
        verified_only=is_verified_only,
    )
    builders = list_builders(db, verified_only=is_verified_only)

    return templates.TemplateResponse(
        request=request,
        name="search.html",
        context={
            "query": q,
            "industry": industry,
            "tech": tech,
            "verified_only": is_verified_only,
            "view_mode": view,
            "deployments": deployments,
            "builders": builders,
            "current_user": current_user,
        },
    )


@router.get("/admin", response_class=HTMLResponse)
def admin_page(
    request: Request,
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db),
):
    if not current_user or not current_user.is_admin:
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)

    pending = (
        db.query(Deployment)
        .filter(Deployment.verification_status == "PENDING")
        .order_by(Deployment.created_at.asc())
        .all()
    )

    total_users = db.query(func.count(User.id)).scalar() or 0
    total_deps = db.query(func.count(Deployment.id)).scalar() or 0
    verified_deps = db.query(func.count(Deployment.id)).filter(Deployment.is_verified.is_(True)).scalar() or 0
    pending_deps = len(pending)
    founding_count = db.query(func.count(Membership.id)).scalar() or 0

    return templates.TemplateResponse(
        request=request,
        name="admin.html",
        context={
            "current_user": current_user,
            "pending_deployments": pending,
            "stats": {
                "total_users": total_users,
                "total_deployments": total_deps,
                "verified_deployments": verified_deps,
                "pending_deployments": pending_deps,
                "total_founding_members": founding_count,
            },
        },
    )


@router.post("/admin/verify/{deployment_id}")
def handle_admin_verify(
    deployment_id: int,
    status: str = Form(...),
    feedback_notes: Optional[str] = Form(None),
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db),
):
    if not current_user or not current_user.is_admin:
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)

    review_in = VerificationReview(status=status, feedback_notes=feedback_notes)
    review_deployment(db, deployment_id, reviewer_id=current_user.id, review_data=review_in)
    return RedirectResponse(url="/admin", status_code=status.HTTP_303_SEE_OTHER)
