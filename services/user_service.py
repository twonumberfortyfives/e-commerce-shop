import os
from datetime import datetime, timezone, timedelta
from typing import Annotated

from fastapi import HTTPException, Depends, Response
from fastapi.security import OAuth2PasswordBearer
from jwt import InvalidTokenError
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from database import models
from serializers.user_serializer import UserCreate, TokenData, User, LoginInput
import jwt

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")
REFRESH_TOKEN_EXPIRE_MINUTES = os.getenv("REFRESH_TOKEN_EXPIRE_MINUTES")


async def create_access_token(data: dict, expires_delta: timedelta):
    expire = datetime.now(timezone.utc) + expires_delta
    data.update({"exp": expire})
    return jwt.encode(payload=data, key=SECRET_KEY, algorithm=ALGORITHM)


async def create_refresh_token(data: dict, expires_delta: timedelta):
    expire = datetime.now(timezone.utc) + expires_delta
    data.update({"exp": expire})
    return jwt.encode(payload=data, key=SECRET_KEY, algorithm=ALGORITHM)


async def get_user_by_username(db: AsyncSession, username: str):
    query = await db.execute(
        select(models.DBUser).filter(models.DBUser.username == username)
    )
    return query.scalars().first()


async def get_current_user(
        token: Annotated[str, Depends(oauth2_scheme)], db: AsyncSession
):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except InvalidTokenError:
        raise credentials_exception
    user = await get_user_by_username(username=token_data.username, db=db)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(
        current_user: Annotated[User, Depends(get_current_user)],
):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


async def login_view(response: Response, login_serializer: LoginInput, db: AsyncSession):
    user = await get_user_by_username(db, login_serializer.username)
    if user:
        access_token_expires = timedelta(minutes=float(ACCESS_TOKEN_EXPIRE_MINUTES))
        access_token = await create_access_token(
            data={"sub": user.username}, expires_delta=access_token_expires
        )
        refresh_token = await create_refresh_token(
            data={"sub": user.email},
            expires_delta=timedelta(minutes=float(REFRESH_TOKEN_EXPIRE_MINUTES))
        )
        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,
            secure=True,
            samesite="none",
        )
        access_token = {
            "access_token": access_token,
            "token_type": "bearer",
        }
        return access_token
    raise HTTPException(
        status_code=400,
        detail="Incorrect username or password",
    )


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


async def hash_password(password: str) -> str:
    return pwd_context.hash(password)


async def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


async def register_view(register_serializer: UserCreate, db: AsyncSession):
    try:
        user_email_match = await db.execute(
            select(models.DBUser).filter(models.DBUser.email == register_serializer.email)
        )
        user_username_match = await db.execute(
            select(models.DBUser).filter(
                models.DBUser.username == register_serializer.username
            )
        )

        if user_email_match.scalars().first():
            raise HTTPException(status_code=400, detail="Email already registered")
        if user_username_match.scalars().first():
            raise HTTPException(status_code=400, detail="Username already registered")

        new_user = models.DBUser(
            username=register_serializer.username,
            email=register_serializer.email,
            password=await hash_password(register_serializer.password),
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
