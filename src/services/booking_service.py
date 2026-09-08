import re
from datetime import date, time, timedelta

NAME_PATTERN = re.compile(r"^[A-Za-zА-Яа-яЁё\s-]+$")

SLOT_MIN_HOUR = 12
SLOT_MAX_HOUR = 22
MAX_BOOKING_DAYS_AHEAD = 90


def validate_name(value: str) -> str:
    name = value.strip()
    if len(name) < 2 or not NAME_PATTERN.fullmatch(name):
        raise ValueError(
            "Имя должно содержать минимум 2 символа и только буквы, пробелы или дефис"
        )
    return name


def validate_phone(value: str) -> str:
    digits = re.sub(r"\D", "", value)
    if len(digits) == 11 and digits[0] in ("7", "8"):
        return value
    raise ValueError(
        "Введите корректный номер: +7XXXXXXXXXX или 8XXXXXXXXXX (10 цифр после кода)"
    )


def validate_booking_date(value: date) -> date:
    today = date.today()
    if value < today:
        raise ValueError("Дата брони не может быть раньше сегодняшнего дня")
    if value > today + timedelta(days=MAX_BOOKING_DAYS_AHEAD):
        raise ValueError(
            f"Дата брони не может быть позднее чем через {MAX_BOOKING_DAYS_AHEAD} дней"
        )
    return value


def validate_booking_time(value: time) -> time:
    if value.minute != 0 or value.second != 0 or value.microsecond != 0:
        raise ValueError(
            "Время брони должно быть ровным часовым слотом (12:00, 13:00, ...)"
        )
    if not (SLOT_MIN_HOUR <= value.hour <= SLOT_MAX_HOUR):
        raise ValueError(
            f"Время брони должно быть в диапазоне "
            f"{SLOT_MIN_HOUR:02d}:00 – {SLOT_MAX_HOUR:02d}:00"
        )
    return value

