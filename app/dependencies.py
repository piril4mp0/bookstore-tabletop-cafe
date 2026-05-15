# review this code
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from app.db.database import SessionLocal


def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    except Exception:
        db.rollback()
        raise SQLAlchemyError("Erro ao realizar operação no banco de dados")
    finally:
        db.close()
