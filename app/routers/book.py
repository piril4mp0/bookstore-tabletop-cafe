from http import HTTPStatus
from fastapi import APIRouter, Depends, Body
from sqlalchemy.orm import Session
from app.dependencies import get_db, get_current_admin_user
from app.schemas.book import BookImport, BookPublic, BookPut, IncreaseBookStock
from app.services.book import BookService
from app.models.user import User as UserModel

router = APIRouter(prefix="/books", tags=["books"])


@router.get("/{isbn}", response_model=BookPublic, status_code=HTTPStatus.OK)
def get_book_by_isbn(isbn: str, db: Session = Depends(get_db)):
	return BookService.fetch_book_and_validate(db, isbn)


@router.get("/", response_model=list[BookPublic], status_code=HTTPStatus.OK)
def get_books(
	db: Session = Depends(get_db),
):
	return BookService.get_books(db)


@router.post("/import", response_model=BookPublic, status_code=HTTPStatus.CREATED)
async def import_book(
	book: BookImport,
	db: Session = Depends(get_db),
	current_user: UserModel = Depends(get_current_admin_user),
):
	return await BookService.import_book_from_open_library(db, book)


@router.patch("/add-stock/{isbn}", response_model=BookPublic, status_code=HTTPStatus.OK)
def add_book_stock(
	isbn: str,
	stock: IncreaseBookStock = Body(),
	db: Session = Depends(get_db),
	current_user: UserModel = Depends(get_current_admin_user),
):
	return BookService.add_book_stock(isbn, stock.stock, db)


@router.put("/{isbn}", response_model=BookPublic, status_code=HTTPStatus.OK)
def edit_book(
	isbn: str,
	updated_book: BookPut = Body(),
	db: Session = Depends(get_db),
	current_user: UserModel = Depends(get_current_admin_user),
):
	return BookService.update_book(updated_book, db, isbn)


@router.delete("/{isbn}", status_code=HTTPStatus.OK)
def remove_book(
	isbn: str,
	db: Session = Depends(get_db),
	current_user: UserModel = Depends(get_current_admin_user),
):
	BookService.remove_book(isbn, db)
	return
