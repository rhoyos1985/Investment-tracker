from app.handlers.error.response_error_exception import ResponseErrorException
from app.handlers.error.testerror import UnifiedValidationException
from fastapi import Request, status
from fastapi.exceptions import RequestValidationError

async def api_validation_error(request: Request, exc: RequestValidationError):
    print(f"api_validation_error: {exc.errors()}")  # Puedes eliminar este print en producción
    raise ResponseErrorException.unprocessable_entity(
        detail="Entity can not be process",
        validation_errors=exc.errors()
    )
