from fastapi import FastAPI, Depends
from fastapi.staticfiles import StaticFiles
from strawberry.fastapi import GraphQLRouter

from api.v1.user import router as user_router
from database.engine import engine
from dependencies.get_db import get_db
from schemas.user_schema import schema

from sqladmin import Admin


app = FastAPI()
admin = Admin(app, engine)


app.include_router(user_router, prefix="/api/v1")

app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")


async def get_context(
    db=Depends(get_db),
):  # initialized context getter func to use it before every resolver calls
    return {"db": db}


graphql_app = GraphQLRouter(schema, context_getter=get_context)

# Add the GraphQL endpoint to FastAPI
app.include_router(graphql_app, prefix="/graphql")


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}
