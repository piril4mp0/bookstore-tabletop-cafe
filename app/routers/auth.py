from http import HTTPStatus
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.dependencies import get_db

from app.schemas.auth import Token, UserCreate, UserLogin, UserPublic
from app.services.auth_service import AuthService


router = APIRouter(prefix="/auth", tags=["login"])


@router.post("/login", response_model=Token, status_code=HTTPStatus.OK)
def user_login(user: UserLogin, db: Session = Depends(get_db)):
    return AuthService.login(user, db)


@router.post("/signup", response_model=UserPublic, status_code=HTTPStatus.CREATED)
def user_signup(user: UserCreate, db: Session = Depends(get_db)):
    return AuthService.register_user(user, db)
