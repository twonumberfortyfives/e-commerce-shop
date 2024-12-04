from fastapi import Depends, APIRouter
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from dependencies.get_db import get_db
from schemas.user_schema import schema
from serializers import user_serializer
from services.user_service import get_all_users, register_view, login_view  # Import your user service


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


@router.get("/register")
async def register(register_serializer: user_serializer.UserCreate, db: AsyncSession = Depends(get_db)):
    return await register_view(register_serializer=register_serializer, db=db)


@router.get("/login", response_model=user_serializer.Token)
async def login(login_serializer: user_serializer.LoginInput, db: AsyncSession = Depends(get_db)):
    return await login_view(login_serializer=login_serializer, db=db)
