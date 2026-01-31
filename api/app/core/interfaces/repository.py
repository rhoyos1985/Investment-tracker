from abc import ABC, abstractmethod
from typing import TypeVar, Generic, Optional, List
from uuid import UUID

T = TypeVar('T')

class BaseRepository(ABC, Generic[T]):
    """Abstract base repository defining standard CRUD operations"""
    
    @abstractmethod
    def create(self, entity: T) -> T:
        """Create a new entity"""
        pass
    
    @abstractmethod
    def get_by_id(self, id: UUID) -> Optional[T]:
        """Get entity by ID"""
        pass
    
    @abstractmethod
    def get_all(self, skip: int = 0, limit: int = 100) -> List[T]:
        """Get all entities with pagination"""
        pass
    
    @abstractmethod
    def update(self, id: UUID, entity: T) -> Optional[T]:
        """Update an existing entity"""
        pass
    
    @abstractmethod
    def delete(self, id: UUID) -> bool:
        """Delete entity by ID"""
        pass
