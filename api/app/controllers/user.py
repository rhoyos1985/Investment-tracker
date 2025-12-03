from app.infrastructure.settings.logger import logger
from app.util.mappers.api_response import ApiResponse
from fastapi import APIRouter, Depends, HTTPException
from app.handlers.error.response_error_exception import ResponseErrorException
from app.util.dtos.user import UserDTO

router = APIRouter()

@router.post("/create-user", tags=["User"], summary="Create a new user")
def create_user(user: UserDTO):
    try:
        print(f"Creating user: {user.username} with email: {user.email}")
        return ApiResponse[UserDTO](api_message="User created successfully", api_data=user)
    except ResponseErrorException:
        logger.error("Error creating user ResponseErrorException")
        raise
    except Exception as e:
        print(f"Unexpected error creating user: {str(e)}")
        #logger.error(f"Unexpected error creating user: {str(e)}")
        raise ResponseErrorException.bad_request("Unexpected error creating user", str(e))
