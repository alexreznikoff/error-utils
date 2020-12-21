from aiohttp.web_exceptions import HTTPError
from aiohttp.web_middlewares import middleware
from aiohttp.web_request import Request
from aiohttp.web_response import Response, json_response

from error_utils.errors import BaseErrorHandler, ExceptionsProcessor, Error


class AiohttpErrorHandler(BaseErrorHandler):
    handle_exception = HTTPError

    def get_error(self, exception: HTTPError) -> Error:
        return Error(status=exception.status, detail={"common": exception.text})


COMMON_ERROR_HANDLERS = [
    AiohttpErrorHandler,
    BaseErrorHandler,
]


def create_error_handling_middleware(exceptions_handler: ExceptionsProcessor) -> middleware:

    @middleware
    async def handle_errors(request: Request, handler) -> Response:
        try:
            return await handler(request)
        except Exception as ex:
            error = exceptions_handler.get_error(ex)
            return json_response(status=error.status, data=error.detail)

    return handle_errors
