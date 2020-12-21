from typing import Any


class BaseError(Exception):
    """Base class for errors."""
    code = 500
    detail = {"error": "Internal error"}

    def __init__(self, code: int = None, detail: Any = None):
        """
        :param code: Http error code
        :param detail: Error detail information
        """
        self.detail = detail or self.detail
        self.code = code or self.code

    def __str__(self):
        return f'Error: code: {self.code}, detail: {self.detail}'


class InternalError(BaseError):
    pass


class AuthorizationError(BaseError):
    code = 401
    detail = {"error": "Authorization error"}


class BadRequest(BaseError):
    code = 400
    detail = {"error": "Bad request"}


class AccessDeniedError(BaseError):
    code = 403
    detail = {"error": "Access denied"}


class NotFoundError(BaseError):
    code = 404
    detail = {"error": "Not found"}
