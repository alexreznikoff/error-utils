from typing import Any

from error_utils.errors.types import ErrorType


class BaseError(Exception):
    """Base class for errors."""
    error_type: str = ErrorType.INTERNAL_ERROR
    code = 500

    def __init__(self, message: str = None, detail: Any = None, code: int = None):
        """
        :param message: Error message
        :param detail: Error detail information
        :param code: Http error code
        """
        super().__init__(message)
        self.message = message or self.error_type
        self.detail = detail
        self.code = code or self.code

    def __str__(self):
        return f'Error: code: {self.code}, message: {self.message}, detail: {self.detail}'


class InternalError(BaseError):
    pass


class AuthorizationError(BaseError):
    error_type = ErrorType.AUTHORIZATION_FAILED
    code = 401


class BadRequest(BaseError):
    error_type = ErrorType.BAD_REQUEST
    code = 400


class AccessDeniedError(BaseError):
    error_type = ErrorType.ACCESS_DENIED
    code = 403


class NotFoundError(BaseError):
    error_type = ErrorType.NOT_FOUND
    code = 404
