import logging

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError

from app.api.routes import health, match, profiles
from app.core.config import get_settings
from app.core.constants import ENGINE_VERSION
from app.services.embeddings.errors import EmbeddingUnavailableError

logging.basicConfig(level=logging.INFO)
app = FastAPI(
    title="Twintro Professional Matching Engine",
    version=ENGINE_VERSION,
    description="Deterministic hybrid professional matching. Optional AI explains computed results.",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=get_settings().cors_origins,
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)
for router in (health.router, profiles.router, match.router):
    app.include_router(router, prefix="/api/v1")


@app.exception_handler(SQLAlchemyError)
async def database_error(request: Request, error: SQLAlchemyError):
    logging.getLogger(__name__).error("Database operation failed: %s", type(error).__name__)
    return JSONResponse(
        status_code=503,
        content={"detail": "Database unavailable. Start PostgreSQL and initialize the schema."},
    )


@app.exception_handler(EmbeddingUnavailableError)
async def embedding_error(request: Request, error: EmbeddingUnavailableError):
    return JSONResponse(status_code=503, content={"detail": str(error)})


@app.exception_handler(Exception)
async def unexpected_error(request: Request, error: Exception):
    logging.getLogger(__name__).exception("Request failed")
    return JSONResponse(
        status_code=503,
        content={"detail": "Matching service unavailable. Check the backend logs and local embedding model."},
    )
