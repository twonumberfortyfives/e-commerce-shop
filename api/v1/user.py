from fastapi import Depends, APIRouter, Response, Request, UploadFile
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from dependencies.get_db import get_db
from serializers import user_serializer
from services.user_service import (
    get_all_users,
    register_view,
    login_view,
    refresh_view,
    logout_view,
    verify_email_view,
    my_profile_view,
    edit_my_profile_view,
)  # Import your user service


router = APIRouter()


# @router.get("/users")
# async def fetch_users(db: AsyncSession = Depends(get_db)):
#     query = """
#         query {
#           getAllUsers {
#             username
#             email
#           }
#         }
#     """
#
#     result = await schema.execute(
#         query, context_value={"db": db}
#     )  # Pass the session to the query
#     return JSONResponse(content=result.data)
#


@router.post("/register", response_model=user_serializer.UserCreateOutput)
async def register(
    register_serializer: user_serializer.UserCreate, db: AsyncSession = Depends(get_db)
):
    return await register_view(register_serializer=register_serializer, db=db)


@router.post("/login", response_model=user_serializer.Token)
async def login(
    response: Response,
    login_serializer: user_serializer.LoginInput,
    db: AsyncSession = Depends(get_db),
):
    return await login_view(response=response, login_serializer=login_serializer, db=db)


@router.post("/logout", response_model=user_serializer.Logout)
async def logout(request: Request, response: Response):
    return await logout_view(request=request, response=response)


@router.post("/refresh")
async def refresh(request: Request, response: Response):
    return await refresh_view(request=request, response=response)


@router.get("/verify", response_model=user_serializer.EmailVerification)
async def verify_email(token: str, db: AsyncSession = Depends(get_db)):
    return await verify_email_view(token=token, db=db)


@router.get("/my-profile", response_model=user_serializer.MyProfile)
async def my_profile(
    request: Request, response: Response, db: AsyncSession = Depends(get_db)
):
    return await my_profile_view(request=request, response=response, db=db)


@router.patch("/my-profile", response_model=user_serializer.MyProfile)
async def edit_my_profile(
    request: Request,
    response: Response,
    username: str = None,
    bio: str = None,
    profile_picture: UploadFile | str = None,
    db: AsyncSession = Depends(get_db),
):
    return await edit_my_profile_view(
        username=username,
        bio=bio,
        profile_picture=profile_picture,
        request=request,
        response=response,
        db=db,
    )
