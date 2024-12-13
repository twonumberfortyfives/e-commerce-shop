from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from dependencies.get_db import get_db

router = APIRouter()


@router.get("/products")
async def something(db: AsyncSession = Depends(get_db)):
    pass
