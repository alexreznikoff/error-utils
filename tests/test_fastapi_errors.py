import pytest
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from pydantic.main import BaseModel
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.testclient import TestClient

from error_utils.errors import InternalError, AccessDeniedError, ExceptionsProcessor
from error_utils.framework_helpers.fastapi import FASTAPI_ERROR_HANDLERS, create_error_handling_middleware


def success():
    return {"test": "ok"}


def internal_error_500():
    raise InternalError("Something went wrong")


def runtime_error():
    raise RuntimeError("Test")


def access_denied_error():
    raise AccessDeniedError(detail={"login": "Forbidden"})


def division_by_zero():
    return 25 / 0


class Body(BaseModel):
    id: int
    user: str


def validation_error(body: Body):
    return body


app = FastAPI()
app.add_middleware(BaseHTTPMiddleware,
                   dispatch=create_error_handling_middleware(ExceptionsProcessor(*FASTAPI_ERROR_HANDLERS)))
app.router.add_api_route("/", success)
app.router.add_api_route("/internal_error_500", internal_error_500)
app.router.add_api_route("/runtime_error", runtime_error)
app.router.add_api_route("/access_denied", access_denied_error)
app.router.add_api_route("/division_by_zero", division_by_zero)
app.router.add_api_route("/validation_error", validation_error, methods=["POST"])


@app.exception_handler(StarletteHTTPException)
async def custom_http_exception_handler(request, exc):
    raise exc


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    raise exc


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


def test_http_error_wrong_method(client):
    resp = client.get("/validation_error")

    assert resp.status_code == 405
    assert resp.json() == {
        "error": "METHOD_NOT_ALLOWED",
        "message": "METHOD_NOT_ALLOWED",
        "detail": None,
    }


def test_validation_error_empty_body(client):
    resp = client.post("/validation_error")

    assert resp.status_code == 400
    assert resp.json() == {
        "error": "VALIDATION_ERROR",
        "message": "VALIDATION_ERROR",
        "detail": [
            {
                "loc": ["body"],
                "msg": "field required",
                "type": "value_error.missing",
            },
        ],
    }


def test_validation_error_wrong_body(client):
    resp = client.post("/validation_error", json={"id": "hello"}, headers={"X-Request-Id": "12345"})

    assert resp.status_code == 400
    assert resp.json() == {
        "error": "VALIDATION_ERROR",
        "message": "VALIDATION_ERROR",
        "detail": [
            {
                "loc": ["body", "id"],
                "msg": "value is not a valid integer",
                "type": "type_error.integer",
            },
            {
                "loc": ["body", "user"],
                "msg": "field required",
                "type": "value_error.missing",
            }
        ]
    }


def test_http_not_found_error(client):
    resp = client.get("/not_found")

    assert resp.status_code == 404
    assert resp.json() == {
        "error": "NOT_FOUND",
        "message": "NOT_FOUND",
        "detail": None,
    }


def test_success_result(client):
    resp = client.get("/")

    assert resp.status_code == 200
    assert resp.json() == {"test": "ok"}


def test_internal_error(client):
    resp = client.get("/internal_error_500")

    assert resp.status_code == 500
    assert resp.json() == {
        "error": "INTERNAL_ERROR",
        "message": "Something went wrong",
        "detail": None,
    }


def test_other_error(client):
    resp = client.get("/runtime_error")

    assert resp.status_code == 500
    assert resp.json() == {
        "error": "INTERNAL_ERROR",
        "message": "Test",
        "detail": None,
    }


def test_access_denied_error(client):
    resp = client.get("/access_denied")

    assert resp.status_code == 403
    assert resp.json() == {
        "error": "ACCESS_DENIED",
        "message": "ACCESS_DENIED",
        "detail": {"login": "Forbidden"},
    }


def test_division_by_zero_error(client):
    resp = client.get("/division_by_zero")

    assert resp.status_code == 500
    assert resp.json() == {
        "error": "INTERNAL_ERROR",
        "message": "division by zero",
        "detail": None,
    }
