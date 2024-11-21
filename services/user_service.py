from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from database import models
from serializers.user_serializer import UserCreate
from passlib.context import CryptContext


async def get_all_users(db: AsyncSession):
    try:
        query = await db.execute(select(models.DBUser))
        all_users = query.scalars().all()
        if all_users:
            return all_users
        raise HTTPException(status_code=404, detail="No users found")
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while fetching the user: {str(exc)}",
        )


async def get_user_by_id(db: AsyncSession, user_id: int):
    try:
        query = await db.execute(
            select(models.DBUser).filter(models.DBUser.id == user_id)
        )
        found_user = query.scalars().first()
        if found_user:
            return found_user
        raise HTTPException(status_code=404, detail="User not found")
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while fetching the user: {str(exc)}",
        )


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


async def hash_password(password: str) -> str:
    return pwd_context.hash(password)


async def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


async def create_user(user_serializer: UserCreate, db: AsyncSession):
    try:
        user_email_match = await db.execute(
            select(models.DBUser).filter(models.DBUser.email == user_serializer.email)
        )
        user_username_match = await db.execute(
            select(models.DBUser).filter(
                models.DBUser.username == user_serializer.username
            )
        )

        if user_email_match.scalars().first():
            raise HTTPException(status_code=400, detail="Email already registered")
        if user_username_match.scalars().first():
            raise HTTPException(status_code=400, detail="Username already registered")

        new_user = models.DBUser(
            username=user_serializer.username,
            email=user_serializer.email,
            password=await hash_password(user_serializer.password),
        )
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)
        return new_user

    except HTTPException as http_exc:
        raise http_exc
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while creating the user: {str(exc)}",
        )
