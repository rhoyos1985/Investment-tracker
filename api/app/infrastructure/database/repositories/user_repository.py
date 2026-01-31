from typing import Optional, List
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.core.interfaces.repository import BaseRepository
from app.infrastructure.database.schemas.user import UserSchema
from app.handlers.error.response_error_exception import ResponseErrorException


class UserRepository(BaseRepository[UserSchema]):
    """Repository for User database operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, entity: UserSchema) -> UserSchema:
        """Create a new user in the database"""
        try:
            self.db.add(entity)
            self.db.commit()
            self.db.refresh(entity)
            return entity
        except IntegrityError as e:
            self.db.rollback()
            if "email" in str(e.orig):
                raise ResponseErrorException.conflict("Email already registered")
            if "username" in str(e.orig):
                raise ResponseErrorException.conflict("Username already taken")
            raise ResponseErrorException.bad_request("Error creating user", str(e))
    
    def get_by_id(self, id: UUID) -> Optional[UserSchema]:
        """Get user by UUID"""
        return self.db.query(UserSchema).filter(UserSchema.id == id).first()
    
    def get_by_email(self, email: str) -> Optional[UserSchema]:
        """Get user by email address"""
        return self.db.query(UserSchema).filter(UserSchema.email == email).first()
    
    def get_by_username(self, username: str) -> Optional[UserSchema]:
        """Get user by username"""
        return self.db.query(UserSchema).filter(UserSchema.username == username).first()
    
    def get_all(self, skip: int = 0, limit: int = 100) -> List[UserSchema]:
        """Get all users with pagination"""
        return self.db.query(UserSchema).offset(skip).limit(limit).all()
    
    def update(self, id: UUID, entity: UserSchema) -> Optional[UserSchema]:
        """Update an existing user"""
        existing_user = self.get_by_id(id)
        if not existing_user:
            return None
        
        for key, value in entity.__dict__.items():
            if not key.startswith('_') and value is not None:
                setattr(existing_user, key, value)
        
        try:
            self.db.commit()
            self.db.refresh(existing_user)
            return existing_user
        except IntegrityError as e:
            self.db.rollback()
            raise ResponseErrorException.bad_request("Error updating user", str(e))
    
    def delete(self, id: UUID) -> bool:
        """Delete user by ID"""
        user = self.get_by_id(id)
        if not user:
            return False
        
        self.db.delete(user)
        self.db.commit()
        return True
    
    def deactivate(self, id: UUID) -> Optional[UserSchema]:
        """Soft delete - deactivate user instead of deleting"""
        user = self.get_by_id(id)
        if not user:
            return None
        
        user.is_active = False
        self.db.commit()
        self.db.refresh(user)
        return user
