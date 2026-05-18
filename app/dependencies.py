# review this code
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from app.db.database import SessionLocal
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status
from app.core.settings import settings
import jwt
from jwt.exceptions import InvalidTokenError
from app.models.user import User as UserModel
from sqlalchemy import select

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def get_db():
    db = SessionLocal()
    try:
        yield db
    except SQLAlchemyError:
        db.rollback()
        raise SQLAlchemyError("Erro ao realizar operação no banco de dados")
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
        
        
def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    """Decodes the JWT token and retrieves the current user."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Assuming you store the user's email or username in the "sub" claim
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        payload_email: str = payload.get("sub")
        if payload_email is None:
            raise credentials_exception
    except InvalidTokenError:
        raise credentials_exception
        
    user = db.scalar(select(UserModel).where(UserModel.email == payload_email))
    if user is None:
        raise credentials_exception
        
    return user


def get_current_admin_user(current_user: UserModel = Depends(get_current_user)) -> UserModel:
    """Checks if the currently authenticated user has admin privileges."""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user doesn't have enough privileges"
        )
    return current_user