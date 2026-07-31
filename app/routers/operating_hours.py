from http import HTTPStatus

from fastapi import APIRouter, Body, Depends, HTTPException, Path
from sqlalchemy.orm import Session

from app.dependencies import get_current_admin_user, get_db
from app.models.user import User as UserModel
from app.schemas.operating_hours import OperatingHoursResponse, OperatingHoursUpdate
from app.services.operating_hours import OperatingHoursService

router = APIRouter(prefix="/operating-hours", tags=["operating-hours"])


@router.get("/", response_model=list[OperatingHoursResponse], status_code=HTTPStatus.OK)
def list_operating_hours(db: Session = Depends(get_db)):
	return OperatingHoursService.get_operating_hours(db)


@router.get(
	"/{day_of_week}",
	response_model=OperatingHoursResponse,
	status_code=HTTPStatus.OK,
)
def get_operating_hours_by_day(
	day_of_week: int = Path(ge=0, le=6), db: Session = Depends(get_db)
):
	hours = OperatingHoursService.get_operating_hours_by_day(db, day_of_week)
	if not hours:
		raise HTTPException(
			status_code=HTTPStatus.NOT_FOUND,
			detail=f"No operating hours configured for day {day_of_week}.",
		)
	return hours


@router.put(
	"/{day_of_week}",
	response_model=OperatingHoursResponse,
	status_code=HTTPStatus.OK,
)
def update_operating_hours(
	day_of_week: int = Path(ge=0, le=6),
	hours_update: OperatingHoursUpdate = Body(),
	db: Session = Depends(get_db),
	current_user: UserModel = Depends(get_current_admin_user),
):
	return OperatingHoursService.upsert_operating_hours(db, day_of_week, hours_update)
