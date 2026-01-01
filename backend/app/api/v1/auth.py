"""Authentication endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from ...auth.security import (
    create_access_token,
    decode_access_token,
    get_password_hash,
    verify_password,
)
from ...core.database import get_db
from ...models.user import Admin, User, MissingPersonReport, FoundPersonReport
from ...schemas.auth import (
    AdminLoginRequest,
    LoginResponse,
    MissingPersonReportRequest,
    FoundPersonReportRequest,
    ReportResponse,
    UserLoginRequest,
    UserRegisterRequest,
)
from sqlalchemy.orm import Session

router = APIRouter()
security = HTTPBearer()


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """Extract and verify current user from token."""
    token = credentials.credentials
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    return payload


@router.post("/user/register", response_model=LoginResponse)
async def register_user(
    payload: UserRegisterRequest,
    db: Session = Depends(get_db),
) -> LoginResponse:
    """Register a new user account."""
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    user = User(
        email=payload.email,
        name=payload.name,
        phone=payload.phone,
        password_hash=get_password_hash(payload.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    token = create_access_token({"sub": str(user.id), "type": "user", "email": user.email})
    return LoginResponse(
        access_token=token,
        user_type="user",
        user_id=user.id,
        username=user.name,
    )


@router.post("/user/login", response_model=LoginResponse)
async def user_login(
    payload: UserLoginRequest,
    db: Session = Depends(get_db),
) -> LoginResponse:
    """Authenticate a user."""
    user = db.query(User).filter(User.email == payload.email).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account disabled")
    
    token = create_access_token({"sub": str(user.id), "type": "user", "email": user.email})
    return LoginResponse(
        access_token=token,
        user_type="user",
        user_id=user.id,
        username=user.name,
    )


@router.post("/admin/login", response_model=LoginResponse)
async def admin_login(
    payload: AdminLoginRequest,
    db: Session = Depends(get_db),
) -> LoginResponse:
    """Authenticate an admin."""
    admin = db.query(Admin).filter(Admin.username == payload.username).first()
    if not admin or not verify_password(payload.password, admin.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    if not admin.is_active:
        raise HTTPException(status_code=403, detail="Account disabled")
    
    token = create_access_token(
        {"sub": str(admin.id), "type": "admin", "username": admin.username, "is_super": admin.is_super_admin}
    )
    return LoginResponse(
        access_token=token,
        user_type="admin",
        user_id=admin.id,
        username=admin.username,
    )


@router.post("/user/report/missing", response_model=ReportResponse)
async def report_missing_person(
    payload: MissingPersonReportRequest,
    current_user: dict | None = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ReportResponse:
    """Submit a missing person report."""
    report = MissingPersonReport(
        user_id=current_user.get("sub") if current_user else None,
        reporter_name=payload.reporter_name,
        reporter_phone=payload.reporter_phone,
        reporter_email=payload.reporter_email,
        reporter_relation=payload.reporter_relation,
        person_name=payload.person_name,
        person_age=payload.person_age,
        person_gender=payload.person_gender,
        person_height=payload.person_height,
        person_weight=payload.person_weight,
        person_build=payload.person_build,
        hair_color=payload.hair_color,
        eye_color=payload.eye_color,
        skin_tone=payload.skin_tone,
        distinctive_features=payload.distinctive_features,
        last_seen_location=payload.last_seen_location,
        last_seen_date=payload.last_seen_date,
        last_seen_time=payload.last_seen_time,
        last_seen_description=payload.last_seen_description,
        clothing_description=payload.clothing_description,
        personal_items=payload.personal_items,
        medical_conditions=payload.medical_conditions,
        vulnerable=payload.vulnerable,
        additional_info=payload.additional_info,
        description=payload.description,
        photo_path=payload.photo_path,
        photo_paths=payload.photo_paths,  # JSON string
        status="pending",
    )
    db.add(report)
    db.commit()
    db.refresh(report)
    return ReportResponse(
        report_id=report.id,
        status="pending",
        message="Missing person report submitted successfully. Authorities will be notified.",
    )


@router.post("/user/report/found", response_model=ReportResponse)
async def report_found_person(
    payload: FoundPersonReportRequest,
    proof_photo_path: str | None = None, # This should ideally be handled via upload or separate logic if it's a file path
    current_user: dict | None = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ReportResponse:
    """Submit a found person report."""
    if not proof_photo_path and not payload.contact_authority:
        raise HTTPException(
            status_code=400,
            detail="Either proof photo or authority contact option must be provided",
        )
    
    report = FoundPersonReport(
        user_id=current_user.get("sub") if current_user else None,
        reporter_name=payload.reporter_name,
        reporter_phone=payload.reporter_phone,
        reporter_email=payload.reporter_email,
        found_location=payload.found_location,
        found_date=payload.found_date,
        found_time=payload.found_time,
        person_description=payload.person_description,
        proof_photo_path=proof_photo_path,
        contact_authority=payload.contact_authority,
        status="pending",
    )
    db.add(report)
    db.commit()
    db.refresh(report)
    
    message = "Found person report submitted successfully."
    if payload.contact_authority:
        message += " Please contact authorities directly with all details."
    
    return ReportResponse(
        report_id=report.id,
        status="pending",
        message=message,
    )

