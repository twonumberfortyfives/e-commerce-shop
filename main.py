from fastapi import FastAPI
from api.v1.user import router as user_router

app = FastAPI()


app.include_router(user_router, prefix='/api/v1')


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}
