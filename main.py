from fastapi import FastAPI
from strawberry.fastapi import GraphQLRouter

from api.v1.user import router as user_router
from schemas.user_schema import schema

app = FastAPI()


app.include_router(user_router, prefix="/api/v1")

graphql_app = GraphQLRouter(schema)

# Add the GraphQL endpoint to FastAPI
app.include_router(graphql_app, prefix="/graphql")


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}
