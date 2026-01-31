import traceback

from fastapi import Request, Response, HTTPException, status
from fastapi.exceptions import RequestValidationError
from typing import Optional
from app.infrastructure.settings.logger import logger

class ResponseErrorException(HTTPException):
    
    def __init__(
        self, 
        status_code: int, 
        detail: str, 
        stack: str,
        validation_errors: list
    ):
        super().__init__(status_code=status_code, detail=detail)
        self.stack = stack
        self.validation_errors = validation_errors
   
   # async def __call__(self, request: Request, response: Response, call_next):
   #     try:
   #         print("Handling error in middleware...")
   #         res = await call_next(request)
   #         return res
   #     except RequestValidationError as ve:
   #         logger.error("❌ Validation Error ResponseErrorException", extra={"error": str(ve), "stack_trace": traceback.format_exc()})
            #return ResponseErrorException.unprocessable_entity("Validation error", stack=traceback.format_exc(), validation_errors=ve.errors())
   #     except Exception as e:
   #         logger.error("❌ Error ResponseErrorException", extra={"error": str(e), "stack_trace": traceback.format_exc()})
            #return ResponseErrorException.internal_error("Internal server error in monitoring middleware")

    @classmethod
    def bad_request(cls, detail: str = "Request error", stack: str = ""):
        """Error 400 - Bad Request"""
        return cls(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail,
            stack=stack,
            validation_errors=[]
        )
    
    @classmethod
    def unauthorized(cls, detail: str = "No authorized", stack: str = ""):
        """Error 401 - Unauthorized"""
        return cls(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            stack=stack,
            validation_errors=[]

        )
    
    @classmethod
    def forbidden(cls, detail: str = "forbidden", stack: str = ""):
        """Error 403 - Forbidden"""
        return cls(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail,
            stack=stack,
            validation_errors=[]
        )
    
    @classmethod
    def not_found(cls, detail: str = "Not Found", stack: str = ""):
        """Error 404 - Not Found"""
        return cls(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail,
            stack=stack,
            validation_errors=[]
        )
    
    @classmethod
    def conflict(cls, detail: str = "Conflict", stack: str = ""):
        """Error 409 - Conflict"""
        return cls(
            status_code=status.HTTP_409_CONFLICT,
            detail=detail,
            stack=stack,
            validation_errors=[]
        )
    
    @classmethod
    def unprocessable_entity(cls, detail: str = "Unprocessable Entity", stack: str = "", validation_errors: list = None):
        """Error 422 - Unprocessable Entity"""
        return cls(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=detail, 
            stack=stack, 
            validation_errors=validation_errors or []
        )
    
    @classmethod
    def internal_error(cls, detail: str = "Internal Server Error", stack: str = ""):
        """Error 500 - Internal Server Error"""
        return cls(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail,
            stack=stack,
            validation_errors=[]
        )
    
    @classmethod
    def service_unavailable(cls, detail: str = "Service unavailable", stack: str = ""):
        """Error 503 - Service Unavailable"""
        return cls(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=detail,
            stack=stack,
            validation_errors=[]
        )
    
    @classmethod
    def from_exception(cls, exc: Exception, detail: str = ""):
        """Creates appropriate error from exception type"""
        stack = traceback.format_exc()
        detail = detail or str(exc)
        
        if isinstance(exc, ValueError):
            return cls.bad_request(detail, stack)
        elif isinstance(exc, PermissionError):
            return cls.forbidden(detail, stack)
        elif isinstance(exc, FileNotFoundError):
            return cls.not_found(detail, stack)
        else:
            return cls.internal_error(detail, stack)

def get_stack_trace() -> str:
    return traceback.format_exc()
