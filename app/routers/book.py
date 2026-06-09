from http import HTTPStatus
from fastapi import APIRouter, Depends, Body
from sqlalchemy.orm import Session
from app.dependencies import get_db

from app.schemas.book import BookImport, BookPublic, BookPut, IncreaseBookStock
from app.services.book import BookService

router = APIRouter(prefix="/books", tags=["books"])

@router.post("/import", response_model=BookPublic, status_code=HTTPStatus.CREATED)
async def import_book(book: BookImport, db: Session = Depends(get_db)):    
    return await BookService.import_book_from_open_library(db, book)

@router.patch("/add-stock/{isbn}", response_model=BookPublic, status_code=HTTPStatus.OK)
def add_book_stock(isbn: str, stock: IncreaseBookStock = Body(), db: Session = Depends(get_db)):
    return BookService.add_book_stock(isbn, stock.stock, db)

@router.put("/edit/{isbn}", response_model=BookPublic, status_code=HTTPStatus.OK)
def edit_book(isbn: str, updated_book: BookPut = Body() , db: Session = Depends(get_db)):
    return BookService.update_book(updated_book,db, isbn)

@router.delete("/remove/{isbn}", status_code=HTTPStatus.OK)
def remove_book(isbn: str, db: Session = Depends(get_db)):
    BookService.remove_book(isbn, db)
    return 


