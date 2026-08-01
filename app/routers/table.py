from http import HTTPStatus

from fastapi import APIRouter, Body, Depends, HTTPException, Path
from sqlalchemy.orm import Session

from app.dependencies import get_current_admin_user, get_db
from app.models.user import User as UserModel
from app.schemas.table import Table, TableCreate, TableUpdate
from app.services.table import TableService

router = APIRouter(prefix="/tables", tags=["tables"])


@router.post("/", response_model=Table, status_code=HTTPStatus.CREATED)
def create_table(
	new_table: TableCreate = Body(),
	db: Session = Depends(get_db),
	current_user: UserModel = Depends(get_current_admin_user),
):
	existing = TableService.get_table_by_number(db, new_table.number)
	if existing:
		raise HTTPException(
			status_code=HTTPStatus.CONFLICT,
			detail=f"Table number {new_table.number} already exists.",
		)
	return TableService.create_table(db, new_table)


@router.get("/", response_model=list[Table], status_code=HTTPStatus.OK)
def list_tables(db: Session = Depends(get_db)):
	return TableService.get_tables(db)


@router.get("/{id}", response_model=Table, status_code=HTTPStatus.OK)
def get_table(id: int = Path(gt=0), db: Session = Depends(get_db)):
	table = TableService.get_table_by_id(db, id)
	if not table:
		raise HTTPException(
			status_code=HTTPStatus.NOT_FOUND, detail="Game table not found"
		)
	return table


@router.put("/{id}", response_model=Table, status_code=HTTPStatus.OK)
def update_table(
	id: int = Path(gt=0),
	table_update: TableUpdate = Body(),
	db: Session = Depends(get_db),
	current_user: UserModel = Depends(get_current_admin_user),
):
	if table_update.number is not None:
		existing = TableService.get_table_by_number(db, table_update.number)
		if existing and existing.id != id:
			raise HTTPException(
				status_code=HTTPStatus.CONFLICT,
				detail=f"Table number {table_update.number} already exists.",
			)

	table = TableService.update_table(db, id, table_update)
	if not table:
		raise HTTPException(
			status_code=HTTPStatus.NOT_FOUND, detail="Game table not found"
		)
	return table


@router.delete("/{id}", status_code=HTTPStatus.NO_CONTENT)
def delete_table(
	id: int = Path(gt=0),
	db: Session = Depends(get_db),
	current_user: UserModel = Depends(get_current_admin_user),
):
	if not TableService.delete_table(db, id):
		raise HTTPException(
			status_code=HTTPStatus.NOT_FOUND, detail="Game table not found"
		)
