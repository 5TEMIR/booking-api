from datetime import date, time, timedelta

import pytest

from services.booking_service import (
    validate_booking_date,
    validate_booking_time,
    validate_name,
    validate_phone,
)


class TestValidateName:
    @pytest.mark.parametrize(
        "value",
        ["Иван", "Maria", "Иван-Мария", "Иван Петров", "  Мария  "],
    )
    def test_valid(self, value: str) -> None:
        assert validate_name(value) == value.strip()

    @pytest.mark.parametrize(
        "value",
        ["", "A", "-", "Иван123", "Иван!", "И", "Anna_"],
    )
    def test_invalid(self, value: str) -> None:
        with pytest.raises(ValueError):
            validate_name(value)


class TestValidatePhone:
    @pytest.mark.parametrize(
        "value",
        ["+79161234567", "89991234567", "79161234567"],
    )
    def test_valid(self, value: str) -> None:
        assert validate_phone(value) == value

    @pytest.mark.parametrize(
        "value",
        ["+7999000000", "12345678901", "8916123456", "abc", ""],
    )
    def test_invalid(self, value: str) -> None:
        with pytest.raises(ValueError):
            validate_phone(value)


class TestValidateBookingDate:
    def test_today_is_valid(self) -> None:
        today = date.today()
        assert validate_booking_date(today) == today

    def test_past_is_invalid(self) -> None:
        with pytest.raises(ValueError):
            validate_booking_date(date.today() - timedelta(days=1))

    def test_90_days_ahead_is_valid(self) -> None:
        value = date.today() + timedelta(days=90)
        assert validate_booking_date(value) == value

    def test_91_days_ahead_is_invalid(self) -> None:
        with pytest.raises(ValueError):
            validate_booking_date(date.today() + timedelta(days=91))


class TestValidateBookingTime:
    @pytest.mark.parametrize(
        "value",
        [time(12, 0), time(19, 0), time(22, 0)],
    )
    def test_valid_slots(self, value: time) -> None:
        assert validate_booking_time(value) == value

    @pytest.mark.parametrize(
        "value",
        [time(11, 0), time(23, 0), time(12, 30), time(13, 0, 30)],
    )
    def test_invalid(self, value: time) -> None:
        with pytest.raises(ValueError):
            validate_booking_time(value)