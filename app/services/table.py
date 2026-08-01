from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.table import GameTable
from app.schemas.table import TableCreate, TableUpdate


class TableService:
	"""TableService handles business logic for GameTable management."""

	@staticmethod
	def create_table(db: Session, table: TableCreate) -> GameTable:
		new_table = GameTable(**table.model_dump())
		db.add(new_table)
		db.commit()
		db.refresh(new_table)
		return new_table

	@staticmethod
	def get_tables(db: Session) -> list[GameTable]:
		stmt = select(GameTable).order_by(GameTable.number)
		return list(db.scalars(stmt).all())

	@staticmethod
	def get_table_by_id(db: Session, id: int) -> GameTable | None:
		return db.get(GameTable, id)

	@staticmethod
	def get_table_by_number(db: Session, number: int) -> GameTable | None:
		stmt = select(GameTable).where(GameTable.number == number)
		return db.scalars(stmt).first()

	@staticmethod
	def update_table(
		db: Session, id: int, table_update: TableUpdate
	) -> GameTable | None:
		table = db.get(GameTable, id)
		if not table:
			return None

		update_data = table_update.model_dump(exclude_unset=True)
		for key, value in update_data.items():
			setattr(table, key, value)
		db.commit()
		db.refresh(table)
		return table

	@staticmethod
	def delete_table(db: Session, id: int) -> bool:
		table = db.get(GameTable, id)
		if not table:
			return False
		db.delete(table)
		db.commit()
		return True
