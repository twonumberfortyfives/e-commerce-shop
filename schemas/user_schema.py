from datetime import datetime

import pytz
import strawberry

from serializers.user_serializer import UserCreate
from services.user_service import get_all_users, get_user_by_id, create_user


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
    @strawberry.mutation(graphql_type=User, description="Create a new user")
    async def create_user(
        self, username: str, email: str, password: str, password_confirm: str, info
    ) -> User:
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
