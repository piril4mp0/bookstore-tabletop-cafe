from http import HTTPStatus

from fastapi import APIRouter, Body, Depends, HTTPException, Path
from sqlalchemy.orm import Session

from app.dependencies import get_current_admin_user, get_db
from app.models.user import User as UserModel
from app.schemas.tag import Tag, TagCreate
from app.services.tag import TagService

router = APIRouter(prefix="/tags", tags=["tags"])


@router.post("/", response_model=Tag, status_code=HTTPStatus.CREATED)
def create_tag(
	new_tag: TagCreate = Body(),
	db: Session = Depends(get_db),
	current_user: UserModel = Depends(get_current_admin_user),
):
	return TagService.create_tag(db, new_tag)


@router.get("/", response_model=list[Tag], status_code=HTTPStatus.OK)
def get_tags(db: Session = Depends(get_db)):
	return TagService.get_tags(db)


@router.get("/{id}", response_model=Tag, status_code=HTTPStatus.OK)
def get_tag(id: int = Path(gt=0), db: Session = Depends(get_db)):
	tag = TagService.get_tag_by_id(db, id)
	if not tag:
		raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Tag not found")
	return tag


@router.delete("/{id}", status_code=HTTPStatus.NO_CONTENT)
def delete_tag(
	id: int = Path(gt=0),
	db: Session = Depends(get_db),
	current_user: UserModel = Depends(get_current_admin_user),
):
	if not TagService.delete_tag(db, id):
		raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Tag not found")
