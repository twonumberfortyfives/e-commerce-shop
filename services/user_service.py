from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from database import models  # Make sure this import works for your models
from serializers.user_serializer import UserCreate
from passlib.context import CryptContext



async def get_all_users(db: AsyncSession):
    query = await db.execute(select(models.DBUser))  # Executes a query to get users
    all_users = query.scalars().all()  # Extract the users from the query result
    if all_users:
        return all_users
    raise HTTPException(status_code=404, detail="No users found")


async def get_user_by_id(db: AsyncSession, user_id: int):
    query = await db.execute(
        select(models.DBUser)
        .filter(models.DBUser.id == user_id)
    )
    found_user = query.scalars().first()
    if found_user:
        return found_user
    raise HTTPException(status_code=404, detail="User not found")


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


async def hash_password(password: str) -> str:
    return pwd_context.hash(password)


async def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


async def create_user(user_serializer: UserCreate, db: AsyncSession):
    existing_user = await db.execute(
        select(models.DBUser).filter(
            (models.DBUser.email == user_serializer.email) |
            (models.DBUser.username == user_serializer.username)
        )
    )
    if not existing_user:
        new_user = models.DBUser(
            username=user_serializer.username,
            email=user_serializer.email,
            password=await hash_password(user_serializer.password),
        )
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)
        return new_user
    raise HTTPException(status_code=401, detail="Account with current email or username already exists")
