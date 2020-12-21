import asyncio

import pytest
from aiohttp import web
from aiohttp.web import Application, json_response
from marshmallow.exceptions import ValidationError

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
        return Error(status=400, detail=exc.messages)


async def success(request):
    return json_response({"test": "ok"})


async def validation_error(request):
    raise ValidationError({"test": ["Test validation error."]})


async def base_error(request):
    raise InternalError(detail={"detail": "Test base error"})


async def other_error(request):
    raise RuntimeError("RuntimeError")


async def access_denied_error(request):
    raise AccessDeniedError()


async def authorization_error(request):
    raise AuthorizationError()


async def rewrite_authorization_error(request):
    raise AuthorizationError(code=403, detail={"error": "You shall not pass!!"})


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
        web.get("/validation_error", validation_error),
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
    assert await resp.json() == {"detail": "Test base error"}


async def test_other_error(client):
    resp = await client.get("/other_error")

    assert resp.status == 500
    assert await resp.json() == {"error": ["RuntimeError"]}


async def test_access_denied_error(client):
    resp = await client.get("/access_denied_error")

    assert resp.status == 403
    assert await resp.json() == {"error": "Access denied"}


async def test_validation_error(client):
    resp = await client.get("/validation_error")

    assert resp.status == 400
    assert await resp.json() == {"test": ["Test validation error."]}


async def test_authorization_error(client):
    resp = await client.get("/authorization_error")

    assert resp.status == 401
    assert await resp.json() == {"error": "Authorization error"}


async def test_rewrite_authorization_error(client):
    resp = await client.get("/rewrite_authorization_error")

    assert resp.status == 403
    assert await resp.json() == {"error": "You shall not pass!!"}


async def test_division_by_zero_error(client):
    resp = await client.get("/division_by_zero_error")

    assert resp.status == 500
    assert await resp.json() == {"error": ["division by zero"]}
