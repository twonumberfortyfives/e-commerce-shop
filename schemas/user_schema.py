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
    @strawberry.field(graphql_type=list[User])
    async def get_all_users(self, info) -> List[User]:
        db = info.context["db"]
        db_users = await get_all_users(db)
        return [User(username=user.username, email=user.email) for user in db_users]


schema = strawberry.Schema(Query)
