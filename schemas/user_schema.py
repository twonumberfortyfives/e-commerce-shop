import strawberry
from typing import List

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from dependencies.get_db import get_db
from services.user_service import get_all_users  # A function you will define to get data from DB


@strawberry.type
class User:
    username: str
    email: str


@strawberry.type
class Query:
    async def get_users_from_db(self, db: AsyncSession) -> List[User]:
        return await get_all_users(db)

    @strawberry.field(graphql_type=User)
    async def get_all_users(self, db: AsyncSession = Depends(get_db)) -> List[User]:
        array_of_users = [User(username=user.username, email=user.email) for user in await get_all_users(db)]
        return array_of_users


schema = strawberry.Schema(Query)
