from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from app.handlers.error.api_validation_error import api_validation_error
from app.infrastructure.settings.logger import logger
from app.handlers.monitoring.api_monitoring import api_monitoring
from app.infrastructure.database.adapters.postgres_db import get_conection_database
from app.handlers.error.response_error_exception import ResponseErrorException
from app.handlers.error.api_error_handler import api_error
from app.controllers import health
from app.controllers import user

app = FastAPI(
    title="Investment Portfolio API",
    description="API for managing investment portfolios and retrieving stock data.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inicializar base de datos al iniciar
@app.on_event("startup")
async def on_startup():
    try:
        get_conection_database()
        logger.info("✅ Connection database success", extra=None)
    except Exception as e:
        logger.error("❌ Connection database error", extra={"error": str(e)})

app.middleware("http")(api_monitoring)

app.exception_handler(RequestValidationError)(api_validation_error)
app.exception_handler(ResponseErrorException)(api_error)

app.include_router(health.router, prefix="/monitoring", tags=["Health"])
app.include_router(user.router, prefix="/user", tags=["User"])
