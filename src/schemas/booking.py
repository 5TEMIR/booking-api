from datetime import date, time
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from models.booking import BookingStatus
from services.booking_service import (
    validate_booking_date,
    validate_booking_time,
    validate_name,
    validate_phone,
)


class BookingBase(BaseModel):
    name: str = Field(
        min_length=2,
        max_length=100,
        title="Имя гостя",
        description="Имя гостя: только буквы, пробелы и дефис, минимум 2 символа",
        examples=["Иван Петров", "Мария-Луиза"],
    )
    phone: str = Field(
        min_length=11,
        max_length=20,
        title="Телефон",
        description="Телефон в российском формате: +7XXXXXXXXXX или 8XXXXXXXXXX (10 цифр после кода)",
        examples=["+79161234567", "89991234567"],
    )
    booking_date: date = Field(
        title="Дата брони",
        description="Дата брони: не раньше сегодняшнего дня и не позднее чем через 90 дней",
        examples=["2026-09-10"],
    )
    booking_time: time = Field(
        title="Время брони",
        description="Время брони: часовые слоты с 12:00 до 22:00 включительно",
        examples=["19:00", "12:00"],
    )
    guests: int = Field(
        ge=1,
        le=12,
        title="Количество гостей",
        description="Количество гостей: от 1 до 12",
        examples=[2, 4],
    )


class BookingCreateSchema(BookingBase):
    @field_validator("name")
    @classmethod
    def name_is_valid(cls, value: str) -> str:
        return validate_name(value)

    @field_validator("phone")
    @classmethod
    def phone_is_valid(cls, value: str) -> str:
        return validate_phone(value)

    @field_validator("booking_date")
    @classmethod
    def booking_date_is_valid(cls, value: date) -> date:
        return validate_booking_date(value)

    @field_validator("booking_time")
    @classmethod
    def booking_time_is_valid(cls, value: time) -> time:
        return validate_booking_time(value)


class BookingSchema(BookingBase):
    model_config = ConfigDict(from_attributes=True)

    id: int = Field(
        title="Идентификатор",
        description="Уникальный идентификатор брони",
        examples=[42],
    )
    status: Literal[BookingStatus.ACTIVE, BookingStatus.CANCELLED] = Field(
        title="Статус",
        description="Статус брони: active | cancelled",
        examples=[BookingStatus.ACTIVE],
    )