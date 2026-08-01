from http import HTTPStatus

from fastapi import APIRouter, Body, Depends, HTTPException, Path
from sqlalchemy.orm import Session

from app.dependencies import get_current_user, get_db
from app.models.user import User as UserModel
from app.schemas.reservation import ReservationCreate, ReservationResponse
from app.services.reservation import ReservationService

router = APIRouter(prefix="/reservations", tags=["reservations"])


@router.post("/", response_model=ReservationResponse, status_code=HTTPStatus.CREATED)
def create_reservation(
	reservation_in: ReservationCreate = Body(),
	db: Session = Depends(get_db),
	current_user: UserModel = Depends(get_current_user),
):
	return ReservationService.create_reservation(db, current_user.id, reservation_in)


@router.get("/", response_model=list[ReservationResponse], status_code=HTTPStatus.OK)
def list_reservations(
	db: Session = Depends(get_db),
	current_user: UserModel = Depends(get_current_user),
):
	if current_user.is_admin:
		return ReservationService.get_reservations(db)
	return ReservationService.get_reservations(db, user_id=current_user.id)


@router.get("/{id}", response_model=ReservationResponse, status_code=HTTPStatus.OK)
def get_reservation(
	id: int = Path(gt=0),
	db: Session = Depends(get_db),
	current_user: UserModel = Depends(get_current_user),
):
	reservation = ReservationService.get_reservation_by_id(db, id)
	if not reservation:
		raise HTTPException(
			status_code=HTTPStatus.NOT_FOUND, detail="Reservation not found."
		)
	if not current_user.is_admin and reservation.user_id != current_user.id:
		raise HTTPException(
			status_code=HTTPStatus.FORBIDDEN,
			detail="Not authorized to view this reservation.",
		)
	return reservation


@router.patch(
	"/{id}/cancel",
	response_model=ReservationResponse,
	status_code=HTTPStatus.OK,
)
def cancel_reservation(
	id: int = Path(gt=0),
	db: Session = Depends(get_db),
	current_user: UserModel = Depends(get_current_user),
):
	reservation = ReservationService.get_reservation_by_id(db, id)
	if not reservation:
		raise HTTPException(
			status_code=HTTPStatus.NOT_FOUND, detail="Reservation not found."
		)
	if not current_user.is_admin and reservation.user_id != current_user.id:
		raise HTTPException(
			status_code=HTTPStatus.FORBIDDEN,
			detail="Not authorized to cancel this reservation.",
		)
	return ReservationService.cancel_reservation(db, reservation)
