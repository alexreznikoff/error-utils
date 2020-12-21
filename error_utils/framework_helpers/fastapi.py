from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException
from starlette.requests import Request
from starlette.responses import Response, JSONResponse
from starlette.status import HTTP_422_UNPROCESSABLE_ENTITY

from error_utils.errors import BaseErrorHandler, Error, ExceptionsProcessor


class FastAPIErrorHandler(BaseErrorHandler):
    handle_exception = HTTPException

    def get_error(self, exception: HTTPException) -> Error:
        return Error(status=exception.status_code, detail={"error": exception.detail})


class ValidationErrorHandler(BaseErrorHandler):
    handle_exception = RequestValidationError

    def get_error(self, exception: RequestValidationError) -> Error:
        return Error(status=HTTP_422_UNPROCESSABLE_ENTITY, detail=exception.errors())


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
            return JSONResponse(status_code=error.status, content=error.detail)

    return handle_errors
