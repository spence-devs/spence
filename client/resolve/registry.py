"""Resolver registry"""

from typing import Optional
from client.resolve.base import Resolver
from client.errors import UnsupportedPlatform


class ResolverRegistry:
    """Dynamic resolver registration"""
    
    def __init__(self):
        self._resolvers: list[Resolver] = []
    
    def register(self, resolver: Resolver) -> None:
        """Register a resolver"""
        self._resolvers.append(resolver)
    
    def get_resolver(self, query: str) -> Optional[Resolver]:
        """Find resolver for query"""
        for resolver in self._resolvers:
            if resolver.can_resolve(query):
                return resolver
        return None
    
    def list_platforms(self) -> list[str]:
        """List registered platforms"""
        return [r.platform_name for r in self._resolvers]
