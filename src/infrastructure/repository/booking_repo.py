from datetime import date, time

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.exceptions import BookingNotFound
from models.booking import Booking, BookingStatus
from schemas.booking import BookingCreateSchema, BookingSchema


class BookingRepository:
    _model: type[Booking] = Booking

    async def get_by_id(
        self,
        session: AsyncSession,
        booking_id: int,
    ) -> BookingSchema:
        query = select(self._model).where(self._model.id == booking_id)

        booking = await session.scalar(query)

        if not booking:
            raise BookingNotFound()

        return BookingSchema.model_validate(booking)

    async def get_all(
        self,
        session: AsyncSession,
        booking_date: date | None = None,
    ) -> list[BookingSchema]:
        query = select(self._model).order_by(
            self._model.booking_date.asc(),
            self._model.booking_time.asc(),
        )

        if booking_date is not None:
            query = query.where(self._model.booking_date == booking_date)

        bookings = await session.scalars(query)

        return [BookingSchema.model_validate(booking) for booking in bookings.all()]

    async def get_active_by_date_and_time(
        self,
        session: AsyncSession,
        booking_date: date,
        booking_time: time,
    ) -> Booking | None:
        query = (
            select(self._model)
            .where(
                self._model.booking_date == booking_date,
                self._model.booking_time == booking_time,
                self._model.status == BookingStatus.ACTIVE,
            )
            .limit(1)
        )

        return await session.scalar(query)

    async def create(
        self,
        session: AsyncSession,
        booking_dto: BookingCreateSchema,
    ) -> BookingSchema:
        booking = self._model(**booking_dto.model_dump())

        session.add(booking)
        await session.flush()

        return BookingSchema.model_validate(booking)

    async def cancel(
        self,
        session: AsyncSession,
        booking_id: int,
    ) -> BookingSchema:
        query = select(self._model).where(self._model.id == booking_id)

        booking = await session.scalar(query)

        if not booking:
            raise BookingNotFound()

        if booking.status != BookingStatus.CANCELLED:
            booking.status = BookingStatus.CANCELLED
            await session.flush()

        return BookingSchema.model_validate(booking)
