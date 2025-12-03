from app.util.mappers.api_response import ApiResponse

API_ERROR_DESCRIPTION = { 
    200: {"model": ApiResponse[str], "description": "Success", "content": {}, "example": {
        "api_message": "Resource found successfully",
        "api_data": "Sample data"
        } 
    },
    400: {"model": ApiResponse[None], "description": "Bad Request", "content": {}, "example": {
        "api_message": "Request error",
        "api_data": None
        } 
    },
    401: {"model": ApiResponse[None], "description": "No authorized", "content": {}, "example": {
        "api_message": "No authorized",
        "api_data": None
        } 
    },
    403: {"model": ApiResponse[None], "description": "Forbidden", "content": {}, "example": {
        "api_message": "forbidden",
        "api_data": None
        }
    },
    404: {"model": ApiResponse[None], "description": "Not Found", "content": {}, "example": {
        "api_message": "Not Found",
        "api_data": None
        }
    },
    409: {"model": ApiResponse[None], "description": "Conflict", "content": {}, "example": {
        "api_message": "Conflict",
        "api_data": None
        }
    },
    422: {"model": ApiResponse[None], "description": "Unprocessable Entity", "content": {}, "example": {
    "api_message": "Unprocessable Entity",
    "api_data": None
        }
    },
    500: {"model": ApiResponse[None], "description": "Internal Server Error", "content": {}, "example": {
        "api_message": "Internal Server Error",
        "api_data": None
        }
    },
    503: {"model": ApiResponse[None], "description": "Service Unavailable", "content": {}, "example": {
        "api_message": "Service Unavailable",
        "api_data": None
        }
    }
}
