from tornado.web import HTTPError

from error_utils.errors import BaseErrorHandler, Error


class TornadoErrorHandler(BaseErrorHandler):
    handle_exception = HTTPError

    def get_error(self, exception: HTTPError) -> Error:
        return Error(status=exception.status_code, detail={"common": exception.log_message})


COMMON_ERROR_HANDLERS = [
    BaseErrorHandler,
    TornadoErrorHandler,
]
