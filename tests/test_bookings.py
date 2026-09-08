from datetime import date, time, timedelta

import pytest
from httpx import AsyncClient

from models.booking import Booking

BASE_URL = "/bookings"


def valid_payload(**overrides) -> dict:
    payload = {
        "name": "Иван Петров",
        "phone": "+79161234567",
        "booking_date": (date.today() + timedelta(days=1)).isoformat(),
        "booking_time": "19:00",
        "guests": 2,
    }
    payload.update(overrides)
    return payload


async def test_create_booking_returns_201(client: AsyncClient) -> None:
    response = await client.post(BASE_URL, json=valid_payload())

    assert response.status_code == 201
    body = response.json()
    assert body["id"] == 1
    assert body["status"] == "active"
    assert body["name"] == "Иван Петров"
    assert body["guests"] == 2


@pytest.mark.parametrize(
    "overrides",
    [
        {"name": "A"},
        {"name": "Иван123"},
        {"phone": "+7999000000"},
        {"phone": "12345678901"},
        {"booking_date": (date.today() - timedelta(days=1)).isoformat()},
        {"booking_date": (date.today() + timedelta(days=91)).isoformat()},
        {"booking_time": "12:30"},
        {"booking_time": "23:00"},
        {"guests": 0},
        {"guests": 13},
    ],
)
async def test_create_booking_invalid_data_returns_422(
    client: AsyncClient,
    overrides: dict,
) -> None:
    response = await client.post(BASE_URL, json=valid_payload(**overrides))

    assert response.status_code == 422


async def test_create_booking_occupied_slot_returns_409(client: AsyncClient) -> None:
    payload = valid_payload()

    first = await client.post(BASE_URL, json=payload)
    assert first.status_code == 201

    second = await client.post(BASE_URL, json=payload)
    assert second.status_code == 409
    assert second.json()["detail"]


async def test_create_booking_cancelled_slot_is_free(client: AsyncClient) -> None:
    payload = valid_payload()

    first = await client.post(BASE_URL, json=payload)
    assert first.status_code == 201

    cancelled = await client.delete(f"{BASE_URL}/{first.json()['id']}")
    assert cancelled.status_code == 200

    second = await client.post(BASE_URL, json=payload)
    assert second.status_code == 201


async def test_get_booking_by_id_returns_200(client: AsyncClient) -> None:
    created = await client.post(BASE_URL, json=valid_payload())
    booking_id = created.json()["id"]

    response = await client.get(f"{BASE_URL}/{booking_id}")

    assert response.status_code == 200
    assert response.json()["id"] == booking_id


async def test_get_booking_not_found_returns_404(client: AsyncClient) -> None:
    response = await client.get(f"{BASE_URL}/999")

    assert response.status_code == 404
    assert response.json() == {"detail": "Booking not found"}


async def test_cancel_booking_returns_200_cancelled(client: AsyncClient) -> None:
    created = await client.post(BASE_URL, json=valid_payload())
    booking_id = created.json()["id"]

    response = await client.delete(f"{BASE_URL}/{booking_id}")

    assert response.status_code == 200
    assert response.json()["status"] == "cancelled"


async def test_cancel_booking_is_idempotent(client: AsyncClient) -> None:
    created = await client.post(BASE_URL, json=valid_payload())
    booking_id = created.json()["id"]

    first = await client.delete(f"{BASE_URL}/{booking_id}")
    second = await client.delete(f"{BASE_URL}/{booking_id}")

    assert first.status_code == 200
    assert second.status_code == 200
    assert second.json()["status"] == "cancelled"


async def test_cancel_booking_not_found_returns_404(client: AsyncClient) -> None:
    response = await client.delete(f"{BASE_URL}/999")

    assert response.status_code == 404
    assert response.json() == {"detail": "Booking not found"}


async def test_get_bookings_filters_by_date(client: AsyncClient) -> None:
    today = date.today().isoformat()
    tomorrow = (date.today() + timedelta(days=1)).isoformat()

    await client.post(
        BASE_URL,
        json=valid_payload(booking_date=today, booking_time="12:00"),
    )
    await client.post(
        BASE_URL,
        json=valid_payload(booking_date=tomorrow, booking_time="13:00"),
    )

    response = await client.get(BASE_URL, params={"date": today})

    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]["booking_date"] == today
    assert body[0]["booking_time"] == "12:00:00"


async def test_get_bookings_empty_list_returns_200(client: AsyncClient) -> None:
    response = await client.get(BASE_URL)

    assert response.status_code == 200
    assert response.json() == []


async def test_get_bookings_displays_past_booking(
    client: AsyncClient,
    session,
) -> None:
    past_date = date.today() - timedelta(days=1)

    booking = Booking(
        name="Иван",
        phone="+79161234567",
        booking_date=past_date,
        booking_time=time(19, 0),
        guests=2,
    )
    session.add(booking)
    await session.commit()

    response = await client.get(BASE_URL)

    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]["booking_date"] == past_date.isoformat()
    assert body[0]["status"] == "active"