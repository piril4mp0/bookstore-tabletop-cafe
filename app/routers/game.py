from http import HTTPStatus
from typing import Optional

from fastapi import APIRouter, Body, Depends, Path, Query
from sqlalchemy.orm import Session
from app.dependencies import get_db
from app.schemas.game import GameCreate, Game
from app.models.game import Game as GameModel

router = APIRouter(prefix="/games", tags=["games"])


### Creates a new Game ###
@router.post("/create", response_model=Game, status_code=HTTPStatus.CREATED)
def create_new_game(new_game: GameCreate = Body(), db: Session = Depends(get_db)):
    game = GameModel(**new_game.model_dump())
    db.add(game)
    db.commit()
    db.refresh(game)
    return game

### Gets all games or games by genre ###
@router.get("/", response_model=list[GameModel], status_code=HTTPStatus.OK)
def get_games(genre: str | None = Query(default=None, lt=255), db: Session = Depends(get_db)): 
    # placeholder #
    games = db.query(GameModel).all()
    return games

### Gets game by ID ###
@router.get("/{id}", response_model=GameModel, status_code=HTTPStatus.OK)
def get_game(id: int = Path(gt=0), db: Session = Depends(get_db)): 
    game = db.query(GameModel).filter(GameModel.id == id).first()
    return game

