from fastapi import Depends, APIRouter
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from dependencies.get_db import get_db
from schemas.user_schema import schema
from services.user_service import get_all_users  # Import your user service


router = APIRouter()


@router.get("/users")
async def fetch_users(db: AsyncSession = Depends(get_db)):
    query = """
        query {
          getAllUsers {
            username
            email
          }
        }
    """

    result = await schema.execute(
        query, context_value={"db": db}
    )  # Pass the session to the query
    return JSONResponse(content=result.data)


#
# @router.get("/users")
# async def fetch_users(db: AsyncSession = Depends(get_db)):
#     return await get_all_users(db)
