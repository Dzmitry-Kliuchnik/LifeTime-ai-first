"""
Custom exception handlers for the FastAPI application.
"""

from typing import Any

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from loguru import logger
from starlette.status import (
    HTTP_400_BAD_REQUEST,
    HTTP_404_NOT_FOUND,
    HTTP_422_UNPROCESSABLE_ENTITY,
    HTTP_500_INTERNAL_SERVER_ERROR,
)


class LifeTimeException(Exception):
    """
    Custom base exception for LifeTime AI application.
    """

    def __init__(
        self,
        message: str,
        status_code: int = HTTP_500_INTERNAL_SERVER_ERROR,
        detail: Any = None,
    ):
        self.message = message
        self.status_code = status_code
        self.detail = detail
        super().__init__(self.message)


class ValidationException(LifeTimeException):
    """Exception for validation errors."""

    def __init__(self, message: str, detail: Any = None):
        super().__init__(
            message=message,
            status_code=HTTP_400_BAD_REQUEST,
            detail=detail,
        )


class NotFoundException(LifeTimeException):
    """Exception for resource not found errors."""

    def __init__(self, message: str, detail: Any = None):
        super().__init__(
            message=message,
            status_code=HTTP_404_NOT_FOUND,
            detail=detail,
        )


def add_exception_handlers(app: FastAPI) -> None:
    """
    Add custom exception handlers to the FastAPI application.

    Args:
        app: FastAPI application instance
    """

    @app.exception_handler(LifeTimeException)
    async def lifetime_exception_handler(
        request: Request, exc: LifeTimeException
    ) -> JSONResponse:
        """Handle custom LifeTime exceptions."""
        logger.error(f"LifeTime exception: {exc.message}")
        logger.error(f"Request: {request.method} {request.url}")

        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": exc.message,
                "detail": exc.detail,
                "status_code": exc.status_code,
            },
        )

    @app.exception_handler(HTTPException)
    async def http_exception_handler(
        request: Request, exc: HTTPException
    ) -> JSONResponse:
        """Handle HTTP exceptions."""
        logger.warning(f"HTTP exception: {exc.detail}")
        logger.warning(f"Request: {request.method} {request.url}")

        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": exc.detail,
                "status_code": exc.status_code,
            },
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        """Handle request validation errors."""
        logger.warning(f"Validation error: {exc.errors()}")
        logger.warning(f"Request: {request.method} {request.url}")

        return JSONResponse(
            status_code=HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "error": "Validation error",
                "detail": exc.errors(),
                "status_code": HTTP_422_UNPROCESSABLE_ENTITY,
            },
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(
        request: Request, exc: Exception
    ) -> JSONResponse:
        """Handle unexpected exceptions."""
        logger.exception(f"Unexpected error: {str(exc)}")
        logger.error(f"Request: {request.method} {request.url}")

        return JSONResponse(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": "Internal server error",
                "detail": "An unexpected error occurred",
                "status_code": HTTP_500_INTERNAL_SERVER_ERROR,
            },
        )
