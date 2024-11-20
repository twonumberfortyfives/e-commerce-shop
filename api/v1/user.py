from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from dependencies.get_db import get_db

from services import user_service


router = APIRouter()


@router.get("/users")
async def get_all_users(db: AsyncSession = Depends(get_db)):
    await user_service.get_all_users(db=db)
