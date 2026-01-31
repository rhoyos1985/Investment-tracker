from typing import Optional, List
from uuid import UUID
from passlib.context import CryptContext

from app.infrastructure.database.repositories.user_repository import UserRepository
from app.infrastructure.database.schemas.user import UserSchema
from app.util.dtos.user import UserDTO, UserResponseDTO
from app.handlers.error.response_error_exception import ResponseErrorException

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserService:
    """Service layer for User business logic"""
    
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository
    
    def create_user(self, user_data: UserDTO) -> UserResponseDTO:
        """Create a new user with hashed password"""
        # Check if email already exists
        if self.user_repository.get_by_email(user_data.email):
            raise ResponseErrorException.conflict("Email already registered")
        
        # Check if username already exists
        if self.user_repository.get_by_username(user_data.username):
            raise ResponseErrorException.conflict("Username already taken")
        
        # Hash password
        hashed_password = pwd_context.hash(user_data.password)
        
        # Create user entity
        user_entity = UserSchema(
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            username=user_data.username,
            email=user_data.email,
            hashed_password=hashed_password,
            is_active=user_data.is_active,
            is_admin=user_data.is_admin
        )
        
        created_user = self.user_repository.create(user_entity)
        return self._to_response_dto(created_user)
    
    def get_user_by_id(self, user_id: UUID) -> UserResponseDTO:
        """Get user by ID"""
        user = self.user_repository.get_by_id(user_id)
        if not user:
            raise ResponseErrorException.not_found(f"User with id {user_id} not found")
        return self._to_response_dto(user)
    
    def get_user_by_email(self, email: str) -> Optional[UserResponseDTO]:
        """Get user by email"""
        user = self.user_repository.get_by_email(email)
        if not user:
            return None
        return self._to_response_dto(user)
    
    def get_all_users(self, skip: int = 0, limit: int = 100) -> List[UserResponseDTO]:
        """Get all users with pagination"""
        users = self.user_repository.get_all(skip, limit)
        return [self._to_response_dto(user) for user in users]
    
    def delete_user(self, user_id: UUID) -> bool:
        """Delete user permanently"""
        if not self.user_repository.get_by_id(user_id):
            raise ResponseErrorException.not_found(f"User with id {user_id} not found")
        return self.user_repository.delete(user_id)
    
    def deactivate_user(self, user_id: UUID) -> UserResponseDTO:
        """Deactivate user (soft delete)"""
        user = self.user_repository.deactivate(user_id)
        if not user:
            raise ResponseErrorException.not_found(f"User with id {user_id} not found")
        return self._to_response_dto(user)
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        return pwd_context.verify(plain_password, hashed_password)
    
    def _to_response_dto(self, user: UserSchema) -> UserResponseDTO:
        """Convert UserSchema to UserResponseDTO"""
        return UserResponseDTO(
            id=str(user.id),
            first_name=user.first_name,
            last_name=user.last_name,
            username=user.username,
            email=user.email,
            is_active=user.is_active,
            is_admin=user.is_admin,
            created_at=user.created_at,
            updated_at=user.updated_at
        )
