import secrets
from datetime import datetime, timedelta
from http import HTTPStatus
from zoneinfo import ZoneInfo

from fastapi import HTTPException
from jwt import encode
from pwdlib import PasswordHash
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.settings import settings
from app.models.refresh_token import RefreshToken as RefreshTokenModel
from app.models.user import User as UserModel
from app.schemas.auth import Token, UserCreate, UserLogin

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.JWT_ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES
REFRESH_TOKEN_EXPIRE_DAYS = settings.REFRESH_TOKEN_EXPIRE_DAYS
pwd_context = PasswordHash.recommended()


class AuthService:
	@staticmethod
	def create_access_token(data: dict) -> str:
		"""Creates an access token for the user."""
		to_encode = data.copy()
		expire = datetime.now(tz=ZoneInfo("UTC")) + timedelta(
			minutes=ACCESS_TOKEN_EXPIRE_MINUTES
		)
		to_encode.update({"exp": expire})
		encoded_jwt = encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
		return encoded_jwt

	@staticmethod
	def create_refresh_token(user_id: int, db: Session) -> str:
		"""Creates and persists a DB-backed refresh token for the user."""
		raw_token = secrets.token_urlsafe(32)
		expires_at = datetime.now(tz=ZoneInfo("UTC")) + timedelta(
			days=REFRESH_TOKEN_EXPIRE_DAYS
		)
		refresh_token_record = RefreshTokenModel(
			token=raw_token,
			user_id=user_id,
			expires_at=expires_at,
			revoked=False,
		)
		db.add(refresh_token_record)
		db.commit()
		return raw_token

	@staticmethod
	def get_password_hash(password: str) -> str:
		"""Returns a hashed version of the password."""
		return pwd_context.hash(password)

	@staticmethod
	def verify_password(plain_password: str, hashed_password: str) -> bool:
		"""Verifies if the plain password matches the hashed password."""
		return pwd_context.verify(plain_password, hashed_password)

	@staticmethod
	def hash_password(plain_password: str) -> str:
		"""Hashes a given password."""
		return pwd_context.hash(plain_password)

	@staticmethod
	def register_user(user: UserCreate, db: Session) -> UserModel:
		"""Registers a new user into the DB."""
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
		"""Login method. Returns an access token and a refresh token."""
		query = select(UserModel).where(UserModel.email == user_login.email)
		user = db.execute(query).scalar_one_or_none()
		if not user:
			raise HTTPException(
				status_code=HTTPStatus.UNAUTHORIZED, detail="Invalid email or password"
			)
		if not AuthService.verify_password(user_login.password, user.password):
			raise HTTPException(
				status_code=HTTPStatus.UNAUTHORIZED, detail="Invalid email or password"
			)

		access_token = AuthService.create_access_token(data={"sub": user.email})
		refresh_token = AuthService.create_refresh_token(user_id=user.id, db=db)
		return Token(
			access_token=access_token,
			refresh_token=refresh_token,
			token_type="bearer",
		)

	@staticmethod
	def refresh_tokens(refresh_token_str: str, db: Session) -> Token:
		"""Rotates the refresh token and returns a new access + refresh token pair."""
		stmt = select(RefreshTokenModel).where(
			RefreshTokenModel.token == refresh_token_str
		)
		token_record = db.execute(stmt).scalar_one_or_none()

		if not token_record or token_record.revoked:
			raise HTTPException(
				status_code=HTTPStatus.UNAUTHORIZED,
				detail="Invalid or expired refresh token",
			)

		now = datetime.now(tz=ZoneInfo("UTC"))
		expires_at = token_record.expires_at
		if expires_at.tzinfo is None:
			expires_at = expires_at.replace(tzinfo=ZoneInfo("UTC"))

		if expires_at < now:
			token_record.revoked = True
			db.commit()
			raise HTTPException(
				status_code=HTTPStatus.UNAUTHORIZED,
				detail="Invalid or expired refresh token",
			)

		# Revoke current token (Refresh Token Rotation)
		token_record.revoked = True

		user = db.scalar(select(UserModel).where(UserModel.id == token_record.user_id))
		if not user:
			db.commit()
			raise HTTPException(
				status_code=HTTPStatus.UNAUTHORIZED,
				detail="User not found",
			)

		new_access_token = AuthService.create_access_token(data={"sub": user.email})
		new_refresh_token = AuthService.create_refresh_token(user_id=user.id, db=db)
		return Token(
			access_token=new_access_token,
			refresh_token=new_refresh_token,
			token_type="bearer",
		)

	@staticmethod
	def revoke_token(refresh_token_str: str, db: Session) -> None:
		"""Revokes a refresh token."""
		stmt = select(RefreshTokenModel).where(
			RefreshTokenModel.token == refresh_token_str
		)
		token_record = db.execute(stmt).scalar_one_or_none()

		if not token_record or token_record.revoked:
			raise HTTPException(
				status_code=HTTPStatus.UNAUTHORIZED,
				detail="Invalid or expired refresh token",
			)

		token_record.revoked = True
		db.commit()
