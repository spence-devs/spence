"""Base resolver interface"""

from abc import ABC, abstractmethod
from typing import Optional
from client.api.track import Track


class Resolver(ABC):
    """Base class for platform resolvers"""
    
    @abstractmethod
    def can_resolve(self, query: str) -> bool:
        """Check if this resolver can handle the query"""
        pass
    
    @abstractmethod
    def resolve(self, query: str) -> Track:
        """Resolve query to track"""
        pass
    
    @abstractmethod
    def search(self, query: str, limit: int = 10) -> list[Track]:
        """Search for tracks"""
        pass
    
    @property
    @abstractmethod
    def platform_name(self) -> str:
        """Platform identifier"""
        pass
