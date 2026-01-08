"""Resolver specific errors"""

from client.errors import ResolverError


class SignatureDecryptionFailed(ResolverError):
    """YouTube signature decryption failed"""
    pass


class ClientIDNotFound(ResolverError):
    """SoundCloud client ID not found"""
    pass


class APIRateLimited(ResolverError):
    """API rate limit exceeded"""
    pass
