import logging

from fastapi import FastAPI

from app.routers.auth import router as auth_router
from app.routers.book import router as books_router
from app.routers.game import router as games_router
from app.routers.menu import router as menu_router
from app.routers.tag import router as tags_router

logging.basicConfig(
	level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)

app = FastAPI()

app.include_router(games_router)
app.include_router(auth_router)
app.include_router(books_router)
app.include_router(tags_router)
app.include_router(menu_router)
