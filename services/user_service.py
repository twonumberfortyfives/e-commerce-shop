from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database import models


async def get_all_users(db: AsyncSession):
    query = await db.execute(
        select(models.DBUser)
    )
    all_users = query.scalars().all()
    return all_users

