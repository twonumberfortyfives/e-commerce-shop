from datetime import datetime

import strawberry

from database.models import DBProduct
from services.product_service import get_all_products


@strawberry.type
class ProductImage:
    id: int
    link: str
    product_id: int


@strawberry.type
class ProductCategory:
    id: int
    name: str
    description: str


@strawberry.type
class Product:
    id: int
    name: str
    description: str | None
    price: float
    discount_price: float | None
    stock: int
    created_at: datetime
    category: "ProductCategory"
    images: list[ProductImage]


async def map_product(product: DBProduct) -> Product:
    return Product(
        id=product.id,
        name=product.name,
        description=product.description,
        price=product.price,
        discount_price=product.discount_price,
        stock=product.stock,
        created_at=product.created_at,
        category=ProductCategory(
            id=product.category.id,
            name=product.category.name,
            description=product.category.description,
        ),
        images=[
            ProductImage(
                id=image.id,
                link=image.link,
                product_id=image.product_id,
            )
            for image in product.images
        ],
    )


@strawberry.type
class Query:
    @strawberry.field(graphql_type=list[Product], description="Get all products")
    async def get_all_products(self, info) -> list[Product]:
        db = info.context["db"]
        db_all_products = await get_all_products(db=db)
        return [await map_product(product=product) for product in db_all_products]


product_schema = strawberry.Schema(query=Query)
