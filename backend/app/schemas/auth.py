"""Authentication schemas."""

from __future__ import annotations

from pydantic import BaseModel, EmailStr, Field


class UserLoginRequest(BaseModel):
    """User login credentials."""

    email: EmailStr
    password: str


class AdminLoginRequest(BaseModel):
    """Admin login credentials."""

    username: str
    password: str


class LoginResponse(BaseModel):
    """Login response with token."""

    access_token: str
    token_type: str = "bearer"
    user_type: str  # "user" or "admin"
    user_id: int
    username: str


class UserRegisterRequest(BaseModel):
    """User registration."""

    email: EmailStr
    password: str = Field(..., min_length=6)
    name: str
    phone: str


class MissingPersonReportRequest(BaseModel):
    """Report a missing person."""

    reporter_name: str
    reporter_phone: str
    reporter_email: str | None = None
    reporter_relation: str | None = None
    person_name: str
    person_age: int | None = None
    person_gender: str | None = None
    person_height: str | None = None
    person_weight: str | None = None
    person_build: str | None = None
    hair_color: str | None = None
    eye_color: str | None = None
    skin_tone: str | None = None
    distinctive_features: str | None = None
    last_seen_location: str | None = None
    last_seen_date: str | None = None
    last_seen_time: str | None = None
    last_seen_description: str | None = None
    clothing_description: str | None = None
    personal_items: str | None = None
    medical_conditions: str | None = None
    vulnerable: bool = False
    additional_info: str | None = None
    description: str | None = None
    photo_path: str | None = None
    photo_paths: str | None = None  # JSON array string


class FoundPersonReportRequest(BaseModel):
    """Report a found person."""

    reporter_name: str
    reporter_phone: str
    reporter_email: str | None = None
    found_location: str
    found_date: str
    found_time: str | None = None
    person_description: str | None = None
    contact_authority: bool = False


class ReportResponse(BaseModel):
    """Response after submitting a report."""

    report_id: int
    status: str
    message: str

