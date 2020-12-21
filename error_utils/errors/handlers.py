import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Type

from error_utils.errors import BaseError


@dataclass
class Error:
    status: int = None
    detail: Any = None


class AbstractErrorHandler(ABC):
    handle_exception = None

    def __init__(self):
        if not self.handle_exception:
            raise NotImplemented

    @abstractmethod
    def get_error(self, exc: Exception) -> Error:
        pass


class BaseErrorHandler(AbstractErrorHandler):
    handle_exception = BaseError

    def get_error(self, exc: BaseError) -> Error:
        return Error(status=exc.code, detail=exc.detail)


class ExceptionsProcessor:
    def __init__(self, *args: Type[AbstractErrorHandler]):
        self.handlers = []
        self.add_handlers(*args)

    def add_handlers(self, *args: Type[AbstractErrorHandler]):
        self.handlers.extend([
            handler if isinstance(handler, AbstractErrorHandler) else handler() for handler in args
        ])

    def get_error(self, exc: Exception) -> Error:
        for handler in self.handlers:
            if isinstance(exc, handler.handle_exception):
                return handler.get_error(exc)

        logging.exception(exc)

        return Error(status=500, detail={"error": exc.args})
