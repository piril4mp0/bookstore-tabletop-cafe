from http import HTTPStatus
from fastapi import APIRouter, Body, Depends, HTTPException, Path, Query
from sqlalchemy.orm import Session
from app.dependencies import get_db, get_current_admin_user
from app.schemas.game import GameCreate, Game, GamePut

from app.services.game import GameService
from app.models.user import User as UserModel

router = APIRouter(prefix="/games", tags=["games"])


@router.post("/", response_model=Game, status_code=HTTPStatus.CREATED)
def create_new_game(
	new_game: GameCreate = Body(),
	db: Session = Depends(get_db),
	current_user: UserModel = Depends(get_current_admin_user),
):
	return GameService.save_game(db, new_game)


@router.get("/", response_model=list[Game], status_code=HTTPStatus.OK)
def get_games(
	genre: str | None = Query(default=None, max_length=255),
	db: Session = Depends(get_db),
):
	return GameService.get_games(db, genre)


@router.get("/{id}", response_model=Game, status_code=HTTPStatus.OK)
def get_game(id: int = Path(gt=0), db: Session = Depends(get_db)):
	game = GameService.get_game_by_id(db, id)
	if not game:
		raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Game not found")
	return game


@router.put("/{id}", response_model=Game, status_code=HTTPStatus.OK)
def update_game(
	id: int = Path(gt=0),
	updated_game: GamePut = Body(),
	db: Session = Depends(get_db),
	current_user: UserModel = Depends(get_current_admin_user),
):
	game = GameService.update_game(db, id, updated_game)
	if not game:
		raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Game not found")
	return game


@router.delete("/{id}", status_code=HTTPStatus.NO_CONTENT)
def delete_game(
	id: int = Path(gt=0),
	db: Session = Depends(get_db),
	current_user: UserModel = Depends(get_current_admin_user),
):
	if not GameService.delete_game(db, id):
		raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Game not found")
