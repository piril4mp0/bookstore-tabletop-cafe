from sys import prefix

from fastapi import FastAPI
from app.routers.game import router as games_router
from app.routers.auth import router as auth_router

app = FastAPI()

app.include_router(games_router)
app.include_router(auth_router)

