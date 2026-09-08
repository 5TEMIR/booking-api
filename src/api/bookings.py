from datetime import date

from fastapi import APIRouter, HTTPException, Query, status

from api.depends import booking_repo, database
from core.exceptions import BookingNotFound, BookingSlotAlreadyTaken
from schemas.booking import BookingCreateSchema, BookingSchema

booking_router = APIRouter()


@booking_router.get(
    "/bookings",
    response_model=list[BookingSchema],
    status_code=status.HTTP_200_OK,
)
async def get_bookings(
    date: date | None = Query(
        default=None,
        description="Фильтр по дате брони, например ?date=2026-08-20",
    ),
) -> list[BookingSchema]:
    async with database.session() as session:
        return await booking_repo.get_all(
            session=session,
            booking_date=date,
        )


@booking_router.post(
    "/bookings",
    response_model=BookingSchema,
    status_code=status.HTTP_201_CREATED,
)
async def create_booking(
    booking_dto: BookingCreateSchema,
) -> BookingSchema:
    try:
        async with database.session() as session:
            occupied_slot = await booking_repo.get_active_by_date_and_time(
                session=session,
                booking_date=booking_dto.booking_date,
                booking_time=booking_dto.booking_time,
            )

            if occupied_slot is not None:
                raise BookingSlotAlreadyTaken(
                    booking_date=booking_dto.booking_date,
                    booking_time=booking_dto.booking_time,
                )

            return await booking_repo.create(
                session=session,
                booking_dto=booking_dto,
            )
    except BookingSlotAlreadyTaken as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=error.message,
        )


@booking_router.get(
    "/bookings/{booking_id}",
    response_model=BookingSchema,
    status_code=status.HTTP_200_OK,
)
async def get_booking(
    booking_id: int,
) -> BookingSchema:
    try:
        async with database.session() as session:
            return await booking_repo.get_by_id(
                session=session,
                booking_id=booking_id,
            )
    except BookingNotFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=BookingNotFound.message,
        )


@booking_router.delete(
    "/bookings/{booking_id}",
    response_model=BookingSchema,
    status_code=status.HTTP_200_OK,
)
async def cancel_booking(
    booking_id: int,
) -> BookingSchema:
    try:
        async with database.session() as session:
            return await booking_repo.cancel(
                session=session,
                booking_id=booking_id,
            )
    except BookingNotFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=BookingNotFound.message,
        )

