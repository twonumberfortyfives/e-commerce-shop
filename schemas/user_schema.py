import strawberry
from services.user_service import get_all_users


@strawberry.type
class User:
    username: str
    email: str


@strawberry.type
class Query:
    users = [DBUser] = strawberry.field(resolver=get_all_users)


schema = strawberry.Schema(Query)
