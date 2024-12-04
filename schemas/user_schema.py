import os
from datetime import datetime, timedelta

import pytz
import strawberry
from fastapi import HTTPException

from serializers.user_serializer import UserCreate, Token, LoginInput
from services.user_service import (
    get_all_users,
    get_user_by_id,
    register_view,
    login_view,
    create_access_token,
)
from dotenv import load_dotenv


load_dotenv()

ACCESS_TOKEN_EXPIRE_MINUTES = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")


@strawberry.type
class User:
    id: int
    username: str
    email: str
    profile_picture: str
    role: str
    phone_number: str | None
    is_verified: bool
    created_at: datetime

    @strawberry.field(name="createdAt")  # This maps to the query field `createdAt`
    def created_at_with_timezone(self) -> str:
        """Format created_at as a string in UTC with 'Z'."""
        if isinstance(self.created_at, str):
            self.created_at = datetime.fromisoformat(self.created_at)

        utc_time = self.created_at.astimezone(pytz.utc)

        return utc_time.isoformat().replace("+00:00", "Z")


@strawberry.type
class Token:
    access_token: str
    token_type: str


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
    @strawberry.field(graphql_type=list[User], description="List of users")
    async def get_all_users(self, info) -> list[User]:
        db = info.context["db"]
        db_users = await get_all_users(db=db)
        return [await map_user(user) for user in db_users]

    @strawberry.field(graphql_type=User, description="Get user by id")
    async def get_user_by_id(self, user_id: int, info) -> User:
        db = info.context["db"]
        found_user = await get_user_by_id(db=db, user_id=user_id)
        return await map_user(found_user)


@strawberry.type
class Mutation:

    @strawberry.mutation(graphql_type=Token, description="login for access token")
    async def login_for_access_token(self, info, username: str, password: str) -> Token:
        db = info.context["db"]
        user = await login_view(db=db, username=username, password=password)
        if not user:
            raise HTTPException(
                status_code=401,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        access_token_expires = timedelta(minutes=float(ACCESS_TOKEN_EXPIRE_MINUTES))
        access_token = create_access_token(
            data={"sub": user.username}, expires_delta=access_token_expires
        )
        return Token(access_token=access_token, token_type="bearer")


schema = strawberry.Schema(query=Query, mutation=Mutation)
