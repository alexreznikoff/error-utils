from typing import Any

import pytest
import tornado.web
from marshmallow import fields, Schema, ValidationError
from sqlalchemy.orm.exc import NoResultFound
from tornado.escape import json_decode, json_encode

from error_utils.errors import AccessDeniedError, BaseErrorHandler, Error, ExceptionsProcessor, InternalError
from error_utils.errors.types import ErrorType
from error_utils.framework_helpers.tornado import TORNADO_ERROR_HANDLERS, handle_error


class ValidationErrorHandler(BaseErrorHandler):
    handle_exception = ValidationError

    def get_error(self, exc: ValidationError) -> Error:
        return Error(
            status=400,
            error_type=ErrorType.VALIDATION_ERROR,
            message=ErrorType.VALIDATION_ERROR,
            detail=exc.messages
        )


processor = ExceptionsProcessor(*TORNADO_ERROR_HANDLERS, ValidationErrorHandler)


class BaseView(tornado.web.RequestHandler):

    def write_error(self, status_code: int, **kwargs: Any) -> None:
        code, data = handle_error(kwargs["exc_info"][1], processor)
        self.set_status(code)
        self.write(json_encode(data))
        return


class SuccessView(BaseView):
    async def get(self):
        self.write(json_encode({"test": "ok"}))


class BaseErrorView(BaseView):
    async def get(self):
        raise InternalError(detail={"detail": "Test base error"})


class TornadoHttpErrorView(BaseView):
    async def get(self):
        raise tornado.web.HTTPError(400, "Invalid signature")


class SqlAlchemyErrorView(BaseView):
    async def get(self):
        raise NoResultFound("Item not found")


class MarshmallowValidationErrorView(BaseView):
    async def post(self):

        class RequestSchema(Schema):
            date = fields.Date(required=True)

        RequestSchema().loads(self.request.body)
        self.write(json_encode({"test": "ok"}))


class AccessDeniedErrorView(BaseView):
    async def get(self):
        raise AccessDeniedError()


class DivizionByZeroView(BaseView):
    async def get(self):
        result = 25 / 0
        self.write(str(result))


application = tornado.web.Application(
    handlers=[
        (r"/", SuccessView),
        (r"/base_error", BaseErrorView),
        (r"/http_error", TornadoHttpErrorView),
        (r"/validation_error", MarshmallowValidationErrorView),
        (r"/access_denied", AccessDeniedErrorView),
        (r"/divizion_by_zero", DivizionByZeroView),
    ]
)


@pytest.fixture
def app():
    return application


async def test_success(http_server_client):
    response = await http_server_client.fetch("/")

    assert response.code == 200
    assert json_decode(response.body) == {"test": "ok"}


async def test_base_error(http_server_client):
    response = await http_server_client.fetch("/base_error", raise_error=False)

    assert response.code == 500
    assert json_decode(response.body) == {
        "error": "INTERNAL_ERROR",
        "message": "INTERNAL_ERROR",
        "detail": {"detail": "Test base error"},
    }


async def test_http_error(http_server_client):
    response = await http_server_client.fetch("/http_error", raise_error=False)

    assert response.code == 400
    assert json_decode(response.body) == {
        "error": "BAD_REQUEST",
        "message": "Invalid signature",
        "detail": None,
    }


async def test_validation_error(http_server_client):
    response = await http_server_client.fetch(
        "/validation_error", method="POST", body='{"wrong": "data"}', raise_error=False
    )

    assert response.code == 400
    assert json_decode(response.body) == {
        "error": "VALIDATION_ERROR",
        "message": "VALIDATION_ERROR",
        "detail": {
            "date": ["Missing data for required field."],
            "wrong": ["Unknown field."],
        },
    }


async def test_access_denied_error(http_server_client):
    response = await http_server_client.fetch("/access_denied", raise_error=False)

    assert response.code == 403
    assert json_decode(response.body) == {
        "error": "ACCESS_DENIED",
        "message": "ACCESS_DENIED",
        "detail": None,
    }


async def test_divizion_by_zero_error(http_server_client):
    response = await http_server_client.fetch("/divizion_by_zero", raise_error=False)

    assert response.code == 500
    assert json_decode(response.body) == {
        "error": "INTERNAL_ERROR",
        "message": "division by zero",
        "detail": None,
    }
