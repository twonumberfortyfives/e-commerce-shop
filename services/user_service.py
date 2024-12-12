import os
import uuid
from datetime import datetime, timezone, timedelta
from typing import Sequence, Any
import aiofiles

from fastapi import HTTPException, Response, Request, UploadFile
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from sqlalchemy import select, Row, RowMapping
from sqlalchemy.ext.asyncio import AsyncSession
from database import models
from serializers.user_serializer import UserCreate, LoginInput
import jwt

from fastapi_mail import FastMail, MessageSchema, ConnectionConfig

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")
REFRESH_TOKEN_EXPIRE_MINUTES = os.getenv("REFRESH_TOKEN_EXPIRE_MINUTES")
MAIL_USERNAME = os.getenv("MAIL_USERNAME")
MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
MAIL_FROM = os.getenv("MAIL_FROM")
MAIL_PORT = os.getenv("MAIL_PORT")
MAIL_SERVER = os.getenv("MAIL_SERVER")
DOMAIN = os.getenv("DOMAIN")

conf = ConnectionConfig(
    MAIL_USERNAME=MAIL_USERNAME,
    MAIL_PASSWORD=MAIL_PASSWORD,
    MAIL_FROM=MAIL_FROM,
    MAIL_PORT=MAIL_PORT,
    MAIL_SERVER="smtp.gmail.com",
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
)


async def create_access_token(data: dict, expires_delta: timedelta) -> str:
    expire = datetime.now(timezone.utc) + expires_delta
    data.update({"exp": expire})
    return jwt.encode(payload=data, key=SECRET_KEY, algorithm=ALGORITHM)


async def create_refresh_token(data: dict, expires_delta: timedelta) -> str:
    expire = datetime.now(timezone.utc) + expires_delta
    data.update({"exp": expire})
    return jwt.encode(payload=data, key=SECRET_KEY, algorithm=ALGORITHM)


async def create_verification_token(email: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(hours=1)
    payload = {"email": email, "exp": expire}
    return jwt.encode(payload=payload, key=SECRET_KEY, algorithm=ALGORITHM)


async def send_verification_email(email: str) -> None:
    token = await create_verification_token(email=email)
    verification_link = f"http://localhost:8000/api/v1/verify?token={token}"
    message = MessageSchema(
        subject="Verification email",
        recipients=[email],
        body=f"Verification link: {verification_link}",
        subtype="plain",
    )
    fm = FastMail(conf)
    await fm.send_message(message)


async def verify_email_view(token: str, db: AsyncSession) -> dict:
    try:
        payload = jwt.decode(jwt=token, key=SECRET_KEY, algorithms=ALGORITHM)
        email = payload.get("email")
        user = await get_user_by_email(email=email, db=db)
        if user.is_verified:
            raise HTTPException(status_code=400, detail="User already verified")
        user.is_verified = True
        await db.commit()
        await db.refresh(user)
        return {"message": "Email verified successfully"}
    except jwt.exceptions.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="An error has been occurred.")


async def get_user_by_username(db: AsyncSession, username: str) -> models.DBUser:
    query = await db.execute(
        select(models.DBUser).filter(models.DBUser.username == username)
    )
    return query.scalars().first()


async def get_user_by_email(db: AsyncSession, email: str) -> models.DBUser:
    query = await db.execute(select(models.DBUser).filter(models.DBUser.email == email))
    return query.scalars().first()


async def login_view(
    response: Response, login_serializer: LoginInput, db: AsyncSession
) -> dict:
    user = await get_user_by_username(db, login_serializer.username)
    if user:
        access_token = await create_access_token(
            data={"sub": user.username},
            expires_delta=timedelta(minutes=float(ACCESS_TOKEN_EXPIRE_MINUTES)),
        )
        refresh_token = await create_refresh_token(
            data={"sub": user.username},
            expires_delta=timedelta(minutes=float(REFRESH_TOKEN_EXPIRE_MINUTES)),
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


async def logout_view(request: Request, response: Response) -> dict:
    access_token = await refresh_view(request=request, response=response)
    if access_token:
        response.delete_cookie("refresh_token")
        return {"message": "Successfully logged out!"}
    raise HTTPException(
        status_code=401, detail="Error has been occurred while logging out"
    )


async def refresh_view(request: Request, response: Response) -> dict:
    auth_header = request.headers.get("Authorization")
    if auth_header:
        access_token = auth_header[len("Bearer "):]
        try:
            payload = jwt.decode(jwt=access_token, key=SECRET_KEY, algorithms=ALGORITHM)
            access_token = {
                "access_token": payload,
                "token_type": "bearer",
            }
            return access_token
        except jwt.exceptions.ExpiredSignatureError:
            pass
        except jwt.exceptions.DecodeError:
            raise HTTPException(status_code=400, detail="Invalid token")

    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise HTTPException(status_code=401, detail="Refresh token missing")
    try:
        payload = jwt.decode(jwt=refresh_token, key=SECRET_KEY, algorithms=ALGORITHM)
        username = payload.get("sub")

        new_access_token = await create_access_token(
            data={"sub": username},
            expires_delta=timedelta(minutes=float(ACCESS_TOKEN_EXPIRE_MINUTES)),
        )
        new_refresh_token = await create_refresh_token(
            data={"sub": username},
            expires_delta=timedelta(minutes=float(REFRESH_TOKEN_EXPIRE_MINUTES)),
        )
        response.set_cookie(
            key="refresh_token",
            value=new_refresh_token,
            httponly=True,
            secure=True,
            samesite="none",
        )
        access_token = {
            "access_token": new_access_token,
            "token_type": "bearer",
        }
        return access_token
    except jwt.exceptions.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Refresh token expired")
    except jwt.exceptions.DecodeError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")


async def get_all_users(db: AsyncSession) -> Sequence[models.DBUser]:
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


async def get_user_by_id(db: AsyncSession, user_id: int) -> Row[Any] | RowMapping:
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


async def register_view(
    register_serializer: UserCreate, db: AsyncSession
) -> models.DBUser:
    try:
        user_email_match = await db.execute(
            select(models.DBUser).filter(
                models.DBUser.email == register_serializer.email
            )
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

        # Create new user
        new_user = models.DBUser(
            username=register_serializer.username,
            email=register_serializer.email,
            password=await hash_password(register_serializer.password),
        )
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)
        await send_verification_email(email=new_user.email)
        return new_user

    except HTTPException as http_exc:
        raise http_exc
    except Exception as exc:
        await db.rollback()  # Rollback the transaction on other errors
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while creating the user: {str(exc)}",
        )


async def get_current_user(
    request: Request, response: Response, db: AsyncSession
) -> models.DBUser:
    access_token = (await refresh_view(request=request, response=response)).get(
        "access_token"
    )
    payload = jwt.decode(jwt=access_token, key=SECRET_KEY, algorithms=ALGORITHM)
    user_username = payload.get("sub")
    return await get_user_by_username(username=user_username, db=db)


async def my_profile_view(
    request: Request, response: Response, db: AsyncSession
) -> models.DBUser:
    return await get_current_user(request=request, response=response, db=db)


async def edit_my_profile_view(
        username: str,
        bio: str,
        profile_picture: UploadFile,
        request: Request,
        response: Response,
        db: AsyncSession,
):
    current_user = await get_current_user(request=request, response=response, db=db)
    if username:
        current_user.username = username
    if bio:
        current_user.bio = bio
    if profile_picture:
        if profile_picture.content_type not in ["image/jpeg", "image/png"]:
            raise HTTPException(status_code=400, detail="Invalid image type")
        os.makedirs("uploads/user_profile_pictures", exist_ok=True)
        image_path = (
            f"uploads/user_profile_pictures/{uuid.uuid4()}.{profile_picture.filename}"
        )
        async with aiofiles.open(image_path, "wb") as file:
            await file.write(await profile_picture.read())
        current_user.profile_picture = f"{DOMAIN}/{image_path}"
    await db.commit()
    await db.refresh(current_user)
    return current_user
