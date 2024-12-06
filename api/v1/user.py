from fastapi import Depends, APIRouter, Response, Request
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from dependencies.get_db import get_db
from schemas.user_schema import schema
from serializers import user_serializer
from services.user_service import get_all_users, register_view, login_view, refresh_view, \
    logout_view  # Import your user service


router = APIRouter()


@router.get("/users")
async def fetch_users(db: AsyncSession = Depends(get_db)):
    query = """
        query {
          getAllUsers {
            username
            email
          }
        }
    """

    result = await schema.execute(
        query, context_value={"db": db}
    )  # Pass the session to the query
    return JSONResponse(content=result.data)


@router.post("/register")
async def register(register_serializer: user_serializer.UserCreate, db: AsyncSession = Depends(get_db)):
    return await register_view(register_serializer=register_serializer, db=db)


@router.post("/login", response_model=user_serializer.Token)
async def login(response: Response, login_serializer: user_serializer.LoginInput, db: AsyncSession = Depends(get_db)):
    return await login_view(response=response, login_serializer=login_serializer, db=db)


@router.post("/logout", response_model=user_serializer.Logout)
async def logout(request: Request, response: Response):
    return await logout_view(request=request, response=response)


@router.post("/refresh")
async def refresh(request: Request, response: Response):
    return await refresh_view(request=request, response=response)
