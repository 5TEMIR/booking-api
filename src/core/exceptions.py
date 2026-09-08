from datetime import date, time
from typing import Final


class BookingNotFound(Exception):
    message: Final[str] = "Booking not found"

    def __init__(self) -> None:
        super().__init__(self.message)


class BookingSlotAlreadyTaken(Exception):
    _ERROR_MESSAGE_TEMPLATE: Final[str] = (
        "Слот {booking_time} на {booking_date} уже занят"
    )

    def __init__(self, booking_date: date, booking_time: time) -> None:
        self.message = self._ERROR_MESSAGE_TEMPLATE.format(
            booking_date=booking_date.isoformat(),
            booking_time=booking_time.strftime("%H:%M"),
        )
        super().__init__(self.message)

