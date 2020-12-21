## Библиотека error-utils

### ChangeLog
0.0.1
  - error_utils.errors.exceptions - Список общих ошибок
  - error_utils.errors.handlers - Обработчики ошибок
  - error_utils.framework_helpers - Пакет с функциями для подключения обработчиков к веб-фреймворкам (aiohttp/fastapi/tornado)


# Установка

```bash
$ pip install error-utils // базовая версия
$ pip install error-utils['fastapi'] // обработчики для fastapi
$ pip install error-utils['aiohttp'] // обработчики для aiohttp
$ pip install error-utils['tornado'] // обработчики для tornado
```

# error_utils.errors - Exceptions для приведения к общему виду
  * BaseError
  * InternalError
  * NotFoundError
  * BadRequest
  * AccessDeniedError
  * AuthorizationError


# error_utils.framework_helpers.aiohttp - Обработчики ошибок для aiohttp

```python
from aiohttp import web

from error_utils.errors import ExceptionsProcessor
from error_utils.framework_helpers.aiohttp import COMMON_ERROR_HANDLERS, create_error_handling_middleware

error_handling_middleware = create_error_handling_middleware(
  ExceptionsProcessor(*COMMON_ERROR_HANDLERS)
)

app = web.Application(middlewares=[
  error_handling_middleware
])
```

# error_utils.framework_helpers.tornado - Обработчики ошибок для tornado

```python
from typing import Any

import tornado.web

from error_utils.errors import ExceptionsProcessor
from error_utils.framework_helpers.tornado import COMMON_ERROR_HANDLERS

exceptions_processor = ExceptionsProcessor(*COMMON_ERROR_HANDLERS)


class BaseView(tornado.web.RequestHandler):
  def write_error(self, status_code: int, **kwargs: Any) -> None:
    error = exceptions_processor.get_error(kwargs["exc_info"][1])
    self.set_status(error.status)
    self.write(error.detail)
    return


class DivizionByZeroView(BaseView):
  async def get(self):
    result = 25 / 0
    self.write(str(result))


application = tornado.web.Application([
  (r"/divizion_by_zero", DivizionByZeroView),
])
```

# Создание кастомного обработчика ошибок

```python
from marshmallow import ValidationError
from error_utils.errors import AbstractErrorHandler, Error, ExceptionsProcessor


# кастомный обработчик ошибок marshmallow.ValidationError
class ValidationErrorHandler(AbstractErrorHandler):
  handle_exception = ValidationError  # задаем исключение для обработки, также будут обработаны все его дети

  def get_error(self, exc: ValidationError) -> Error:
    return Error(status=400, detail=exc.messages)


exc_processor = ExceptionsProcessor()
exc_processor.add_handlers(ValidationErrorHandler)

# пример использования
try:
  raise ValidationError({"test": ["Test validation error."]})
except Exception as exc:
  error = exc_processor.get_error(exc)
  print(error.status)  # 400
  print(error.detail)  # {"test": ["Test validation error."]}
```
