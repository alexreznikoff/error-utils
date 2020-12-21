from typing import Tuple

from tornado.web import HTTPError

from error_utils.errors import BaseErrorHandler, Error, ExceptionsProcessor
from error_utils.errors.types import ErrorType


class TornadoErrorHandler(BaseErrorHandler):
    handle_exception = HTTPError

    def get_error(self, exception: HTTPError) -> Error:
        return Error(
            status=exception.status_code,
            error_type=ErrorType.BAD_REQUEST,
            message=exception.log_message,
        )


COMMON_ERROR_HANDLERS = [
    BaseErrorHandler,
    TornadoErrorHandler,
]


def handle_error(exception: Exception, processor: ExceptionsProcessor) -> Tuple[int, dict]:
    error = processor.get_error(exc=exception)
    data = dict(error=error.error_type, message=error.message, detail=error.detail)
    return error.status, data
