from fastapi.exceptions import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.integrations.open_library import fetch_book_from_open_library
from app.models.book import Book
from app.schemas.book import BookImport, BookPut


class BookService:
	@staticmethod
	async def import_book_from_open_library(
		db: Session, book: BookImport
	) -> Book | None:
		isbn_exists = BookService._get_book_from_db(db, book.isbn)
		if isbn_exists:
			raise HTTPException(
				status_code=409,
				detail=f"Book ISBN: {book.isbn} already exists in the database.",
			)
		new_book: Book = await fetch_book_from_open_library(book.isbn, book.stock)
		db.add(new_book)
		db.commit()
		db.refresh(new_book)
		return new_book

	@staticmethod
	def add_book_stock(isbn: str, stock: int, db: Session) -> Book | None:
		book = BookService.fetch_book_and_validate(db, isbn)
		book.stock += stock
		db.commit()
		db.refresh(book)
		return book

	@staticmethod
	def update_book(updated_book: BookPut, db: Session, target_isbn: str) -> Book:
		book_db = BookService.fetch_book_and_validate(db, target_isbn)
		update_data = updated_book.model_dump(exclude_unset=True)
		for key, value in update_data.items():
			setattr(book_db, key, value)
		db.commit()
		db.refresh(book_db)
		return book_db

	@staticmethod
	def remove_book(isbn: str, db: Session) -> bool | None:
		book = BookService.fetch_book_and_validate(db, isbn)
		db.delete(book)
		db.commit()
		return True

	@staticmethod
	def _get_book_from_db(db: Session, isbn: str) -> Book:
		return db.scalar(select(Book).where(Book.isbn == isbn))

	@staticmethod
	def fetch_book_and_validate(db: Session, isbn: str) -> Book:
		book = BookService._get_book_from_db(db, isbn)
		if not book:
			raise HTTPException(status_code=404, detail="Book not found on database")
		return book

	@staticmethod
	def get_books(db: Session) -> list[Book]:
		return list(db.scalars(select(Book)).all())
