from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from . import config

from . import models

from . import routers

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await models.create_table()
    yield


def create_app(settings=None):
    if not settings:
        settings = config.get_settings()
    app = FastAPI(lifespan=lifespan)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    models.init_db(settings)
    routers.init_router(app)

    return app
