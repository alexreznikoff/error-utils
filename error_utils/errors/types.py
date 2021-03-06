from enum import Enum


class ErrorType(str, Enum):
    ACCESS_DENIED = "ACCESS_DENIED"
    AUTHORIZATION_FAILED = "AUTHORIZATION_FAILED"
    BAD_REQUEST = "BAD_REQUEST"
    INTERNAL_ERROR = "INTERNAL_ERROR"
    NOT_FOUND = "NOT_FOUND"
    VALIDATION_ERROR = "VALIDATION_ERROR"
