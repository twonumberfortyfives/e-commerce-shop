from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from database import models  # Make sure this import works for your models


async def get_all_users(db: AsyncSession):
    query = await db.execute(select(models.DBUser))  # Executes a query to get users
    all_users = query.scalars().all()  # Extract the users from the query result
    return all_users
