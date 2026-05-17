from datetime import datetime, timedelta
from http import HTTPStatus
from zoneinfo import ZoneInfo

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.core.settings import settings
from pwdlib import PasswordHash
from app.schemas.auth import Token, UserCreate, UserLogin
from app.models.user import User as UserModel  # Ensure this model exists

from jwt import encode

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.JWT_ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES
pwd_context = PasswordHash.recommended()


class AuthService:
    @staticmethod
    def create_access_token(data: dict) -> str:
        """Creates an access token for the user
        _summary_
        Args:
            data (dict): _description_

        Returns:
            str: _description_
        """
        to_encode = data.copy()
        expire = datetime.now(tz=ZoneInfo("UTC")) + timedelta(
            minutes=ACCESS_TOKEN_EXPIRE_MINUTES
        )
        to_encode.update({"exp": expire})
        encoded_jwt = encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt

    @staticmethod
    def get_password_hash(password: str) -> str:
        """Returns a hashed version of the password
        _summary_

        Args:
            password (str): _description_

        Returns:
            str: _description_
        """
        return pwd_context.hash(password)

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verifies if the plain password matches the hashed password
        _summary_
        Args:
            plain_password (str): _description_
            hashed_password (str): _description_

        Returns:
            bool: _description_
        """
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def hash_password(plain_password) -> str:
        return pwd_context.hash(plain_password)

    @staticmethod
    def register_user(user: UserCreate, db: Session):
        query = select(UserModel).where(UserModel.email == user.email)
        user_exists = db.execute(query).scalar_one_or_none()
        if user_exists:
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST,
                detail="User with this email already exists",
            )
        user.password = AuthService.hash_password(user.password)
        new_user = UserModel(**user.model_dump())
        db.add(new_user)
        db.commit()
        return new_user

    @staticmethod
    def login(user_login: UserLogin, db: Session) -> Token:
        query = select(UserModel).where(UserModel.email == email)
        user = db.execute(query).scalar_one_or_none()
        if not user:
            raise HTTPException(
                status_code=HTTPStatus.UNAUTHORIZED, detail="Invalid email or password"
            )
        if not AuthService.verify_password(user_login.password, user.hashed_password):
            raise HTTPException(
                status_code=HTTPStatus.UNAUTHORIZED, detail="Invalid email or password"
            )

        access_token = AuthService.create_access_token(data={"sub": user.email})
        return Token(access_token=access_token, token_type="bearer")
