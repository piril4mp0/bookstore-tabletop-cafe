# review this code
from sqlalchemy.orm import Session
from app.db.database import SessionLocal


def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    except Exception:
        db.rollback()
    finally:
        db.close()
