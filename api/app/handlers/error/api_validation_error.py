from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from app.util.mappers.api_response import ApiResponse
from app.infrastructure.settings.logger import logger


async def api_validation_error(request: Request, exc: RequestValidationError):
    """Handler for Pydantic validation errors - returns JSONResponse directly"""
    error_messages = []
    
    for error in exc.errors():
        field = error["loc"][-1] if error["loc"] else "unknown field"
        error_type = error["type"]
        msg = error["msg"]
        
        if error_type == "missing":
            error_messages.append(f"Field '{field}' is required")
        elif error_type == "string_too_short":
            min_length = error.get("ctx", {}).get("min_length", "?")
            error_messages.append(f"Field '{field}' must have at least {min_length} characters")
        elif error_type == "string_too_long":
            max_length = error.get("ctx", {}).get("max_length", "?")
            error_messages.append(f"Field '{field}' cannot exceed {max_length} characters")
        elif error_type == "value_error.email":
            error_messages.append(f"Field '{field}' must be a valid email")
        elif error_type == "value_error":
            error_messages.append(f"{msg}")
        else:
            error_messages.append(f"Error in field '{field}': {msg}")
    
    logger.warning("Validation error", extra={"errors": error_messages, "url": str(request.url)})
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=ApiResponse[str](
            api_message="Validation error",
            api_data=None,
            errors=error_messages
        ).model_dump()
    )
