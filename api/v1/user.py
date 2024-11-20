from fastapi import APIRouter

router = APIRouter()


@router.get("/products", tags=["products"])
async def get_products():
    return [{"id": 1, "name": "Laptop"}, {"id": 2, "name": "Phone"}]
