from app.handlers.error.response_error_exception import ResponseErrorException

ERROR_TYPES = {
    "400": lambda: ResponseErrorException.bad_request("Request bad syntax"),
    "401": lambda: ResponseErrorException.unauthorized("Invalid authentication"),
    "403": lambda: ResponseErrorException.forbidden("Access forbidden"),
    "404": lambda: ResponseErrorException.not_found("Resource not found"),
    "409": lambda: ResponseErrorException.conflict("Resource conflict"),
    "422": lambda: ResponseErrorException.unprocessable_entity("Unprocessable entity"),
    "500": lambda: ResponseErrorException.internal_error("Internal server error"),
    "503": lambda: ResponseErrorException.service_unavailable("Service unavailable")
}
