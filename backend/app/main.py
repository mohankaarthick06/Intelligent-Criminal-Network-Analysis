from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .core.config import settings
from .core.logging_config import logger
from .core.exceptions import AppException, app_exception_handler
from .routes import (
    health,
    datasets,
    identity,
    anomalies,
    graph,
    model_evaluation
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"{settings.APP_NAME} v{settings.APP_VERSION} starting up.")
    logger.info(f"Raw data dir: {settings.RAW_DATA_DIR}")
    logger.info(f"Models dir: {settings.MODELS_DIR}")
    yield

def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description="Modular data science backend for Intelligent Criminal Network Analysis.",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan
    )

    # CORS configuration
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Register custom exception handler
    app.add_exception_handler(AppException, app_exception_handler)

    # Register routers
    app.include_router(health.router)
    app.include_router(datasets.router)
    app.include_router(identity.router)
    app.include_router(anomalies.router)
    app.include_router(graph.router)
    app.include_router(model_evaluation.router)

    return app

app = create_app()
