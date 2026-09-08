from collections.abc import AsyncIterator

from sqlalchemy.ext.asyncio import AsyncSession

from infrastructure.database import SQLiteDatabase
from infrastructure.repository.booking_repo import BookingRepository

database = SQLiteDatabase()
booking_repo = BookingRepository()


async def get_session() -> AsyncIterator[AsyncSession]:
    async with database.session() as session:
        yield session

