from http import HTTPStatus
from fastapi import APIRouter, Body, Depends, HTTPException, Path, Query
from sqlalchemy.orm import Session
from app.dependencies import get_db
from app.schemas.game import GameCreate, Game, GamePut

from app.services.GameService import GameService

router = APIRouter(prefix="/games", tags=["games"])


### Creates a new Game ###
@router.post("/", response_model=Game, status_code=HTTPStatus.CREATED)
def create_new_game(new_game: GameCreate = Body(), db: Session = Depends(get_db)):
    return GameService.save_game(db, new_game)


### Gets all games or games by genre ###
@router.get("/", response_model=list[Game], status_code=HTTPStatus.OK)
def get_games(
    genre: str | None = Query(default=None, max_length=255),
    db: Session = Depends(get_db),
):
    return GameService.get_games(db, genre)


### Gets game by ID ###
@router.get("/{id}", response_model=Game, status_code=HTTPStatus.OK)
def get_game(id: int = Path(gt=0), db: Session = Depends(get_db)):
    game = GameService.get_game_by_id(db, id)
    if not game:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Game not found")
    return game


### PUT game by ID ###
@router.put("/{id}", response_model=Game, status_code=HTTPStatus.OK)
def update_game(
    id: int = Path(gt=0), updated_game: GamePut = Body(), db: Session = Depends(get_db)
):
    game = GameService.update_game(db, id, updated_game)
    if not game:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Game not found")
    return game


### DELETE game by ID ###
@router.delete("/{id}", status_code=HTTPStatus.NO_CONTENT)
def delete_game(id: int = Path(gt=0), db: Session = Depends(get_db)):
    if not GameService.delete_game(db, id):
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Game not found")
