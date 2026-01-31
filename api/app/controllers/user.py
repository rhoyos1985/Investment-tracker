from app.infrastructure.settings.logger import logger
from app.util.mappers.api_response import ApiResponse
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.handlers.error.response_error_exception import ResponseErrorException
from app.util.dtos.user import UserDTO, UserResponseDTO
from app.infrastructure.database.adapters.postgres_db import get_conection_database
from app.infrastructure.database.repositories.user_repository import UserRepository
from app.core.services.user import UserService

router = APIRouter()


def get_user_service(db: Session = Depends(get_conection_database)) -> UserService:
    """Dependency injection for UserService"""
    repository = UserRepository(db)
    return UserService(repository)


@router.post("/create-user", tags=["User"], summary="Create a new user", response_model=ApiResponse[UserResponseDTO])
def create_user(user: UserDTO, service: UserService = Depends(get_user_service)):
    try:
        created_user = service.create_user(user)
        logger.info(f"User created: {created_user.username}", extra={"user_id": created_user.id})
        return ApiResponse[UserResponseDTO](api_message="User created successfully", api_data=created_user)
    except ResponseErrorException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error creating user: {str(e)}", extra={"error": str(e)})
        raise ResponseErrorException.bad_request("Unexpected error creating user", str(e))
