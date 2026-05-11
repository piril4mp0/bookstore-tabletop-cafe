from sys import prefix

from fastapi import FastAPI
from app.routers.game import router as games_router

app = FastAPI()

app.include_router(games_router)