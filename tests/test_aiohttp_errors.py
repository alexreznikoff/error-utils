import asyncio

import pytest
from aiohttp import web
from aiohttp.web import Application, json_response
from marshmallow import Schema, fields
from marshmallow.exceptions import ValidationError

from error_utils.errors.types import ErrorType
from error_utils.framework_helpers.aiohttp import COMMON_ERROR_HANDLERS, create_error_handling_middleware
from error_utils.errors import (
    AccessDeniedError,
    AuthorizationError,
    Error,
    ExceptionsProcessor,
    InternalError,
)
from error_utils.errors.handlers import BaseErrorHandler


class ValidationErrorHandler(BaseErrorHandler):
    handle_exception = ValidationError

    def get_error(self, exc: ValidationError) -> Error:
        return Error(
            status=400,
            error_type=ErrorType.VALIDATION_ERROR,
            message=ErrorType.VALIDATION_ERROR,
            detail=exc.messages
        )


async def success(request):
    return json_response({"test": "ok"})


async def validation_error(request):
    class RequestSchema(Schema):
        date = fields.Date(required=True)

    RequestSchema().load(await request.json())
    return json_response({"test": "ok"})


async def base_error(request):
    raise InternalError("Something went wrong")


async def other_error(request):
    raise RuntimeError("RuntimeError")


async def access_denied_error(request):
    raise AccessDeniedError()


async def authorization_error(request):
    raise AuthorizationError()


async def rewrite_authorization_error(request):
    raise AuthorizationError(code=403, message="You shall not pass",
                             detail={"login": "does not exists or blocked"})


async def division_by_zero_error(request):
    return 25 / 0


@pytest.fixture
def app():
    app = Application(
        middlewares=[
            create_error_handling_middleware(
                ExceptionsProcessor(ValidationErrorHandler, *COMMON_ERROR_HANDLERS)
            )
        ]
    )
    app.add_routes([
        web.get("/", success),
        web.get("/base_error", base_error),
        web.get("/other_error", other_error),
        web.get("/access_denied_error", access_denied_error),
        web.post("/validation_error", validation_error),
        web.get("/authorization_error", authorization_error),
        web.get("/rewrite_authorization_error", rewrite_authorization_error),
        web.get("/division_by_zero_error", division_by_zero_error),
    ])
    return app


@pytest.fixture
def client(app, aiohttp_client, loop: asyncio.AbstractEventLoop):
    return loop.run_until_complete(aiohttp_client(app))


async def test_success(client):
    resp = await client.get("/")

    assert resp.status == 200
    assert await resp.json() == {"test": "ok"}


async def test_base_error(client):
    resp = await client.get("/base_error")

    assert resp.status == 500
    assert await resp.json() == {
        "error": "INTERNAL_ERROR",
        "message": "Something went wrong",
        "detail": None
    }


async def test_other_error(client):
    resp = await client.get("/other_error")

    assert resp.status == 500
    assert await resp.json() == {
        "error": "INTERNAL_ERROR",
        "message": "RuntimeError",
        "detail": None,
    }


async def test_access_denied_error(client):
    resp = await client.get("/access_denied_error")

    assert resp.status == 403
    assert await resp.json() == {
        "error": "ACCESS_DENIED",
        "message": "ACCESS_DENIED",
        "detail": None
    }


async def test_validation_error(client):
    resp = await client.post("/validation_error", json={"wrong": "field"})

    assert resp.status == 400
    assert await resp.json() == {
        "error": "VALIDATION_ERROR",
        "message": "VALIDATION_ERROR",
        "detail": {
            "date": ["Missing data for required field."],
            "wrong": ["Unknown field."],
        },
    }


async def test_authorization_error(client):
    resp = await client.get("/authorization_error")

    assert resp.status == 401
    assert await resp.json() == {
        "error": "AUTHORIZATION_FAILED",
        "message": "AUTHORIZATION_FAILED",
        "detail": None,
    }


async def test_rewrite_authorization_error(client):
    resp = await client.get("/rewrite_authorization_error")

    assert resp.status == 403
    assert await resp.json() == {
        "error": "AUTHORIZATION_FAILED",
        "message": "You shall not pass",
        "detail": {"login": "does not exists or blocked"},
    }


async def test_division_by_zero_error(client):
    resp = await client.get("/division_by_zero_error")

    assert resp.status == 500
    assert await resp.json() == {
        "error": "INTERNAL_ERROR",
        "message": "division by zero",
        "detail": None,
    }
