from fastapi import FastAPI

from banban.api.routers import router

app = FastAPI()

app.include_router(router)