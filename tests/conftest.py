import os

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine, AsyncSession
from sqlalchemy.pool import StaticPool

os.environ["APP_NAME"] = "Test App"
os.environ["APP_VERSION"] = "test"
os.environ["ENV"] = "test"
os.environ["LOG_LEVEL"] = "INFO"
os.environ["ORIGINS"] = "*"
os.environ["ROOT_PATH"] = ""
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"

from api.depends import get_session
from infrastructure.database import Base
from main import create_app

TEST_ENGINE = create_async_engine(
    "sqlite+aiosqlite:///:memory:",
    poolclass=StaticPool,
)

TEST_SESSION_FACTORY = async_sessionmaker(
    bind=TEST_ENGINE,
    expire_on_commit=False,
    class_=AsyncSession,
)


@pytest_asyncio.fixture(autouse=True)
async def prepared_db():
    async with TEST_ENGINE.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with TEST_ENGINE.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def app():
    return create_app()


@pytest_asyncio.fixture
async def session():
    async with TEST_SESSION_FACTORY() as test_session:
        yield test_session


@pytest_asyncio.fixture
async def client(app, session):
    async def override_get_session():
        yield session

    app.dependency_overrides[get_session] = override_get_session

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as test_client:
        yield test_client

    app.dependency_overrides.clear()