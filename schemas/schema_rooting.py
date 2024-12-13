import strawberry
from schemas.user_schema import Query as UserQuery
from schemas.product_schema import Query as ProductQuery


@strawberry.type
class Query(UserQuery, ProductQuery):
    pass


schema = strawberry.Schema(query=Query)
