from typing import Optional
from app.handlers.error.response_error_exception import ResponseErrorException
from fastapi.responses import JSONResponse
from fastapi import Request, HTTPException
from app.util.mappers.api_response import ApiResponse
from app.infrastructure.settings.logger import logger
from app.util.dtos.extra_logger_information import HttpProcessInformation
from app.util.mappers.logger_mapper import LoggerMapper

async def api_error(request: Request, exc: ResponseErrorException):
    print("Handling API error...")
    stack: Optional[str] = None
    if hasattr(exc, 'stack') and exc.stack:
         stack = f"stack_trace: {exc.stack}"

    error_messages = []
    print(f"Exception details: {exc.detail}")
    if hasattr(exc, 'validation_errors') and exc.validation_errors:
        for error in exc.errors():
            field = error["loc"][-1] if error["loc"] else "campo desconocido"
            error_type = error["type"]
            msg = error["msg"]
        
            if error_type == "missing":
                error_messages.append(f"El campo '{field}' es obligatorio")
            elif error_type == "string_too_short":
                min_length = error.get("ctx", {}).get("min_length", "?")
                error_messages.append(f"El campo '{field}' debe tener al menos {min_length} caracteres")
            elif error_type == "string_too_long":
                max_length = error.get("ctx", {}).get("max_length", "?")
                error_messages.append(f"El campo '{field}' no puede tener más de {max_length} caracteres")
            elif error_type == "value_error.email":
                error_messages.append(f"El campo '{field}' debe ser un email válido")
            elif error_type == "value_error":
                error_messages.append(f"{msg}")
            else:
                error_messages.append(f"Error en el campo '{field}': {msg}")

    request_information = HttpProcessInformation(
        method=request.method, 
        url=str(request.url), 
        client_host=request.client.host if request.client else None, 
        user_agent=request.headers.get('user-agent'), 
        status=exc.status_code, 
        latency_ms="N/A")

    extra_data = LoggerMapper(extra_data=request_information).to_log_format()
    logger.error(
        f"{exc.detail}",
        extra={"stack": stack, **extra_data}
    )
    return JSONResponse(
        status_code=exc.status_code,
        content=ApiResponse[str](
            api_message=exc.detail,
            api_data=None,
            errors= error_messages if error_messages.__len__() > 0 else None
        ).dict()
    )
