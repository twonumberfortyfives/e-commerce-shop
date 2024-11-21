from datetime import datetime

import strawberry
from typing import List, Optional

from serializers.user_serializer import UserCreate
from services.user_service import get_all_users, get_user_by_id, \
    create_user  # A function you will define to get data from DB


@strawberry.type
class User:
    id: int
    username: str
    email: str
    profile_picture: str
    role: str
    phone_number: str
    is_verified: bool
    created_at: datetime


async def map_user(found_user) -> User:
    """Helper function to map a database user object to the User type."""
    return User(
        id=found_user.id,
        username=found_user.username,
        email=found_user.email,
        profile_picture=found_user.profile_picture,
        role=found_user.role,
        phone_number=found_user.phone_number,
        is_verified=found_user.is_verified,
        created_at=found_user.created_at,
    )


@strawberry.type
class Query:
    @strawberry.field(graphql_type=List[User], description="List of users")
    async def get_all_users(self, info) -> List[User]:
        db = info.context["db"]
        db_users = await get_all_users(db=db)
        return [
            await map_user(user)
            for user in db_users
        ]

    @strawberry.field(graphql_type=User, description="Get user by id")
    async def get_user_by_id(self, user_id: int, info) -> User:
        db = info.context["db"]
        found_user = await get_user_by_id(db=db, user_id=user_id)
        return await map_user(found_user)


@strawberry.type
class Mutation:
    @strawberry.mutation(description="Create a new user")
    async def create_user(self, username: str, email: str, password: str, password_confirm: str, info) -> User:
        db = info.context["db"]
        user_serializer = UserCreate(
            username=username,
            email=email,
            password=password,
            password_confirm=password_confirm,
        )
        new_user = await create_user(user_serializer=user_serializer, db=db)
        return await map_user(new_user)


schema = strawberry.Schema(query=Query, mutation=Mutation)
