"""User and admin authentication models."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String, Boolean
from sqlalchemy.orm import relationship

from .base import Base


class User(Base):
    """User accounts for public reporting."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    phone = Column(String(20))
    name = Column(String(255), nullable=False)
    password_hash = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class Admin(Base):
    """Admin accounts for system management."""

    __tablename__ = "admins"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    is_super_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class MissingPersonReport(Base):
    """Reports submitted by users for missing persons."""

    __tablename__ = "missing_person_reports"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=True)
    reporter_name = Column(String(255), nullable=False)
    reporter_phone = Column(String(20), nullable=False)
    reporter_email = Column(String(255))
    reporter_relation = Column(String(50))  # Relationship to missing person
    person_name = Column(String(255), nullable=False)
    person_age = Column(Integer)
    person_gender = Column(String(32))
    person_height = Column(String(50))  # Height in cm or feet
    person_weight = Column(String(50))  # Weight in kg or lbs
    person_build = Column(String(50))  # slim, average, athletic, heavy
    hair_color = Column(String(32))
    eye_color = Column(String(32))
    skin_tone = Column(String(32))
    distinctive_features = Column(String(1000))  # Tattoos, scars, etc.
    last_seen_location = Column(String(512))
    last_seen_date = Column(String(64))
    last_seen_time = Column(String(20))
    last_seen_description = Column(String(2000))  # Circumstances
    clothing_description = Column(String(1000))
    personal_items = Column(String(500))  # Phone, wallet, etc.
    medical_conditions = Column(String(1000))
    vulnerable = Column(Boolean, default=False)  # Elderly, child, disabled
    additional_info = Column(String(2000))
    description = Column(String(2000))  # General description
    photo_path = Column(String(512))  # Primary photo
    photo_paths = Column(String(2000))  # JSON array of additional photos
    status = Column(String(50), default="pending")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class FoundPersonReport(Base):
    """Reports submitted by users when they find someone."""

    __tablename__ = "found_person_reports"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=True)
    reporter_name = Column(String(255), nullable=False)
    reporter_phone = Column(String(20), nullable=False)
    reporter_email = Column(String(255))
    found_location = Column(String(512), nullable=False)
    found_date = Column(String(64), nullable=False)
    found_time = Column(String(20))
    person_description = Column(String(2000))
    proof_photo_path = Column(String(512))
    contact_authority = Column(Boolean, default=False)
    authority_contacted = Column(Boolean, default=False)
    status = Column(String(50), default="pending")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

