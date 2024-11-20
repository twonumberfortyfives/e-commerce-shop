import datetime

import pytz
from sqlalchemy import Column, Integer, String, func, DateTime, Boolean
from sqlalchemy.dialects.postgresql import ENUM

from database.engine import Base
from enum import Enum as PyEnum


class Role(PyEnum):
    admin = "admin"
    user = "user"
    moderator = "moderator"


class DBUser(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False, unique=True, index=True)
    username = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    profile_picture = Column(String, nullable=False)
    role = Column(ENUM(Role), nullable=False, default=Role.user)
    phone_number = Column(String, nullable=False)
    is_verified = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime, default=datetime.datetime.now(tz=pytz.timezone('UTC')))
