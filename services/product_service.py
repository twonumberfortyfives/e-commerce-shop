from typing import Sequence

from database import models
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from database.models import DBProduct


async def get_all_products(
    db: AsyncSession
) -> Sequence[DBProduct]:
    query = await db.execute(
        select(models.DBProduct)
        .outerjoin(models.DBProductCategory, models.DBProduct.category_id == models.DBProductCategory.id)
        .options(selectinload(models.DBProduct.category))
        .outerjoin(models.DBProductImage, models.DBProductImage.product_id == models.DBProduct.id)
        .options(selectinload(models.DBProduct.images))
        .distinct()
        .order_by(models.DBProduct.name.desc())
    )
    all_products = query.scalars().all()
    return all_products
