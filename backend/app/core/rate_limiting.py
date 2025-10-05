"""
Rate limiting middleware and decorators for API endpoints.
"""

import time
from collections import defaultdict, deque
from functools import wraps
from typing import Dict, Optional

from fastapi import HTTPException, Request, status


class RateLimiter:
    """
    Simple in-memory rate limiter using sliding window algorithm.
    In production, use Redis or another distributed cache.
    """

    def __init__(self):
        # Store for each client: deque of request timestamps
        self.clients: Dict[str, deque] = defaultdict(deque)

    def is_allowed(self, client_id: str, limit: int, window_seconds: int) -> bool:
        """
        Check if client is allowed to make a request.

        Args:
            client_id: Unique identifier for the client (IP, user ID, etc.)
            limit: Maximum number of requests allowed
            window_seconds: Time window in seconds

        Returns:
            True if request is allowed, False otherwise
        """
        now = time.time()
        client_requests = self.clients[client_id]

        # Remove old requests outside the window
        while client_requests and client_requests[0] <= now - window_seconds:
            client_requests.popleft()

        # Check if limit is exceeded
        if len(client_requests) >= limit:
            return False

        # Add current request
        client_requests.append(now)
        return True

    def get_remaining_requests(
        self, client_id: str, limit: int, window_seconds: int
    ) -> int:
        """Get number of remaining requests for client."""
        now = time.time()
        client_requests = self.clients[client_id]

        # Remove old requests outside the window
        while client_requests and client_requests[0] <= now - window_seconds:
            client_requests.popleft()

        return max(0, limit - len(client_requests))

    def get_reset_time(self, client_id: str, window_seconds: int) -> Optional[float]:
        """Get time when rate limit resets for client."""
        client_requests = self.clients[client_id]
        if not client_requests:
            return None
        return client_requests[0] + window_seconds


# Global rate limiter instance
rate_limiter = RateLimiter()


def get_client_id(request: Request) -> str:
    """
    Extract client identifier from request.
    In production, you might want to use authenticated user ID.
    """
    # Use IP address as client identifier
    client_ip = request.client.host if request.client else "unknown"

    # You could also use user ID if authenticated
    # user_id = getattr(request.state, 'user_id', None)
    # return f"user:{user_id}" if user_id else f"ip:{client_ip}"

    return f"ip:{client_ip}"


def rate_limit(
    limit: int = 100,
    window_seconds: int = 3600,
    error_message: str = "Rate limit exceeded",
):
    """
    Decorator for rate limiting endpoints.

    Args:
        limit: Maximum number of requests allowed
        window_seconds: Time window in seconds (default: 1 hour)
        error_message: Error message to return when rate limit is exceeded

    Example:
        @rate_limit(limit=10, window_seconds=60)  # 10 requests per minute
        async def my_endpoint():
            pass
    """

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract request from kwargs (FastAPI dependency injection)
            request = None
            for arg in args:
                if isinstance(arg, Request):
                    request = arg
                    break

            if not request:
                # Try to find request in kwargs
                for key, value in kwargs.items():
                    if isinstance(value, Request):
                        request = value
                        break

            if request:
                client_id = get_client_id(request)

                if not rate_limiter.is_allowed(client_id, limit, window_seconds):
                    reset_time = rate_limiter.get_reset_time(client_id, window_seconds)
                    headers = {
                        "X-RateLimit-Limit": str(limit),
                        "X-RateLimit-Remaining": "0",
                    }
                    if reset_time:
                        headers["X-RateLimit-Reset"] = str(int(reset_time))

                    raise HTTPException(
                        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                        detail=error_message,
                        headers=headers,
                    )

                # Note: FastAPI doesn't easily allow modifying response headers in decorators
                # You'd need to use Response object or middleware for this

            return await func(*args, **kwargs)

        return wrapper

    return decorator


# Predefined rate limiters for different endpoint types
def user_read_rate_limit():
    """Rate limit for user read operations (more permissive)."""
    return rate_limit(
        limit=300,  # 300 requests per hour for read operations
        window_seconds=3600,
        error_message="Too many user read requests. Please try again later.",
    )


def user_write_rate_limit():
    """Rate limit for user write operations (more restrictive)."""
    return rate_limit(
        limit=50,  # 50 requests per hour for write operations
        window_seconds=3600,
        error_message="Too many user modification requests. Please try again later.",
    )


def user_auth_rate_limit():
    """Rate limit for authentication-related operations (very restrictive)."""
    return rate_limit(
        limit=10,  # 10 requests per hour for auth operations
        window_seconds=3600,
        error_message="Too many authentication requests. Please try again later.",
    )


# Middleware to add rate limiting headers to all responses
async def rate_limiting_middleware(request: Request, call_next):
    """
    Middleware to add rate limiting information to response headers.
    This is a more comprehensive approach than the decorator.
    """
    response = await call_next(request)

    # Add general rate limiting headers
    client_id = get_client_id(request)

    # For read operations
    remaining_reads = rate_limiter.get_remaining_requests(client_id, 300, 3600)
    response.headers["X-RateLimit-Read-Remaining"] = str(remaining_reads)

    # For write operations
    remaining_writes = rate_limiter.get_remaining_requests(client_id, 50, 3600)
    response.headers["X-RateLimit-Write-Remaining"] = str(remaining_writes)

    return response
