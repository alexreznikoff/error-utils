from fastapi.exceptions import RequestValidationError
from inflection import parameterize, underscore
from starlette.exceptions import HTTPException
from starlette.requests import Request
from starlette.responses import Response, JSONResponse
from starlette.status import HTTP_400_BAD_REQUEST

from error_utils.errors import BaseErrorHandler, Error, ExceptionsProcessor
from error_utils.errors.types import ErrorType


class FastAPIErrorHandler(BaseErrorHandler):
    handle_exception = HTTPException

    def get_error(self, exception: HTTPException) -> Error:
        return Error(
            status=exception.status_code,
            error_type=underscore(parameterize(exception.detail)).upper(),
            message=underscore(parameterize(exception.detail)).upper(),
        )


class ValidationErrorHandler(BaseErrorHandler):
    handle_exception = RequestValidationError

    def get_error(self, exception: RequestValidationError) -> Error:
        return Error(
            status=HTTP_400_BAD_REQUEST,
            error_type=ErrorType.VALIDATION_ERROR,
            message=ErrorType.VALIDATION_ERROR,
            detail=exception.errors()
        )


COMMON_ERROR_HANDLERS = [
    FastAPIErrorHandler,
    ValidationErrorHandler,
    BaseErrorHandler,
]


def create_error_handling_middleware(exceptions_handler: ExceptionsProcessor = None):

    async def handle_errors(request: Request, handler) -> Response:
        try:
            return await handler(request)
        except Exception as ex:
            error = exceptions_handler.get_error(ex)
            data = dict(error=error.error_type, message=error.message, detail=error.detail)
            return JSONResponse(status_code=error.status, content=data)

    return handle_errors
