from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime, Boolean, Float, ForeignKey
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.orm import relationship

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


class DBProductImage(Base):
    __tablename__ = "product_images"

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
        nullable=False,
        unique=True,
        index=True,
    )
    link = Column(String, nullable=False)
    product_id = Column(
        Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False
    )
    product = relationship("DBProduct", back_populates="images")


class DBProductCategory(Base):
    __tablename__ = "product_categories"

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
        nullable=False,
        unique=True,
        index=True,
    )
    name = Column(String(length=255), nullable=False)
    description = Column(String(length=500), nullable=True)
    products = relationship("DBProduct", back_populates="category")


class DBProduct(Base):
    __tablename__ = "products"

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
        nullable=False,
        unique=True,
        index=True,
    )
    name = Column(String(length=255), nullable=False)
    description = Column(String(length=255), nullable=True)
    price = Column(Float, nullable=False)
    discount_price = Column(Float, nullable=True)
    stock = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, default=lambda: datetime.utcnow(), nullable=False)
    category_id = Column(Integer, ForeignKey("product_categories.id"), nullable=False)

    images = relationship(
        "DBProductImage", back_populates="product", cascade="all, delete-orphan"
    )
    category = relationship("DBProductCategory", back_populates="products")
