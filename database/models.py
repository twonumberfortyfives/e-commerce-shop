from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.dialects.postgresql import ENUM

from database.engine import Base
from enum import Enum as PyEnum


class Role(PyEnum):
    admin = "admin"
    user = "user"
    moderator = "moderator"


class DBUser(Base):
    __tablename__ = "users"

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
        nullable=False,
        unique=True,
        index=True,
    )
    username = Column(String, nullable=False, unique=True)
    bio = Column(String(length=500), nullable=True)
    password = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    profile_picture = Column(String, nullable=False, default="default.jpg")
    role = Column(ENUM(Role), nullable=False, default=Role.user)
    phone_number = Column(String, nullable=True)
    is_verified = Column(Boolean, nullable=False, default=False)
    created_at = Column(
        DateTime,
        default=lambda: datetime.utcnow(),  # Use UTC and make it offset-naive
        nullable=False,
    )
