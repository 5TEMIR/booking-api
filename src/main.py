import asyncio
import logging

import uvicorn
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from api.bookings import booking_router
from core.config import settings

logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    app_options: dict = {}
    if settings.ENV.lower() == "prod":
        app_options = {
            "docs_url": None,
            "redoc_url": None,
        }
    if settings.LOG_LEVEL in ("DEBUG", "INFO"):
        app_options["debug"] = True

    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        root_path=settings.ROOT_PATH,
        **app_options,
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(booking_router, tags=["Bookings"])

    return app


app = create_app()


async def main_run() -> None:
    config = uvicorn.Config(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
    )
    server = uvicorn.Server(config=config)
    await server.serve()


if __name__ == "__main__":
    logger.debug(f"database url: {settings.DATABASE_URL}")
    asyncio.run(main_run())

