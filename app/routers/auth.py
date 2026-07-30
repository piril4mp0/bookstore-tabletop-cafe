from http import HTTPStatus
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.dependencies import get_db

from app.schemas.auth import Token, UserCreate, UserLogin, UserPublic
from app.services.auth import AuthService


from fastapi.security import OAuth2PasswordRequestForm


router = APIRouter(prefix="/auth", tags=["login"])


@router.post("/login", response_model=Token, status_code=HTTPStatus.OK)
def user_login(
	form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
	user_login = UserLogin(email=form_data.username, password=form_data.password)
	return AuthService.login(user_login, db)


@router.post("/signup", response_model=UserPublic, status_code=HTTPStatus.CREATED)
def user_signup(user: UserCreate, db: Session = Depends(get_db)):
	return AuthService.register_user(user, db)
