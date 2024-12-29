import traceback
from collections.abc import Iterable
from typing import Any, TypeVar

from rest_framework.exceptions import APIException, ValidationError
from rest_framework.response import Response
from rest_framework.utils.serializer_helpers import ReturnDict, ReturnList
from rest_framework.views import exception_handler

from errors import codes
from errors.codes import status_code_mapping
from errors.error import MailerError
from errors.models import Error
from errors.serializers import ErrorSerializer
from server.logger_settings import logger

T = TypeVar("T")


def prepare_errors(exc: ValidationError | dict) -> dict[str, Any]:
    field_details: dict[str, Any] = {}

    errors: dict  # TODO: тут сложности с типизацией _Detail, ErrorDetail
    if isinstance(exc, ValidationError):
        assert not isinstance(exc.detail, list)
        errors = exc.detail
    else:
        # в случае, если рекурсивно передаем ошибку
        errors = exc

    for field_name, field_errors in errors.items():
        if isinstance(field_errors, list):
            for error in field_errors:
                if isinstance(error, dict):
                    # если поле вложенное (содержит несколько полей с ошибками)
                    # можно воспроизвести, если послать post на /pct/pcr/
                    field_details[field_name] = prepare_errors(error)

                else:
                    field_details[field_name] = field_errors

    return field_details


def flatten(list_of_lists: Iterable[Iterable[T]]) -> list[T]:
    """Extract nested lists of elements into a single list of elements.

    Example:
    -------
    .. code-block:: python

       flatten([[1, 2], [3, 4]]) == [1, 2, 3, 4]
    """
    return [element for sublist in list_of_lists for element in sublist]


def process_validation_error(exc: ValidationError) -> str:
    """Обработка ошибок валидации сериализаторов."""
    ui_description: str = ""

    if isinstance(exc.detail, list):
        # Формируем строку, убедившись что каждый элемент списка преобразован в строку
        """Когда поле сериализатора не прошло валидацию.

        Проверяем, что detail является строкой или словарем и имеет длину больше 0.
        """

        ui_description = "\n".join(
            str(detail)
            for detail in exc.detail
            if isinstance(detail, dict | str) and len(detail)
        )

    elif isinstance(exc.detail, ReturnList):
        # Используется для list serializer
        errors = [
            f'Поле "{field}": {"; ".join(flatten(detail))}'
            for details in exc.detail
            for field, detail in details.items()  # type: ignore  # noqa: PGH003
        ]
        ui_description = "\n".join(set(errors))
        logger.info("ReturnList error")

    elif isinstance(exc.detail, ReturnDict | dict):
        """Когда required поле сериализатора не присутствует в запросе"""
        ui_description = "\n".join(
            [
                f'Поле "{field}": {"; ".join(map(str, errors))}'
                for field, errors in prepare_errors(exc).items()
            ],
        )

    return ui_description


def db_saving_exception_handler(
    exc: Exception | MailerError, context: dict
) -> Response:
    response = exception_handler(exc, context)

    stacktrace = "".join(traceback.format_exception(None, exc, exc.__traceback__))
    logger.critical(stacktrace)
    description_for_users = (
        "На сервере произошла внутренняя ошибка. Обратитесь в службу поддержки."
    )

    db_err = Error(
        error_code=codes.unhandled_error,
        description_for_devs=f"{exc}",
        description_for_users=description_for_users,
        stacktrace=stacktrace,
        handled_gracefully=True,
    )

    if isinstance(exc, MailerError):
        db_err.description_for_devs = exc.description_for_devs
        db_err.description_for_users = exc.description_for_users
        db_err.error_code = exc.error_code
        db_err.save()

        code = (
            status_code_mapping[exc.error_code]
            if exc.error_code in status_code_mapping
            else exc.error_code
        )
        return Response(ErrorSerializer(db_err).data, status=code)

    if isinstance(exc, ValidationError):
        db_err.description_for_users = process_validation_error(exc)
    elif response and response.data.get("detail"):
        if response.data["detail"] == "Not found.":
            # TODO: добавить сохранение этого в ДБ
            response.data[
                "description_for_devs"
            ] = f'{context["view"].get_view_name()}with pk={context["kwargs"]["pk"]} not found'
            response.data[
                "description_for_users"
            ] = f'Объект {context["view"].basename} с id={context["kwargs"]["pk"]} не найден'
            del response.data["detail"]
            return response

        assert isinstance(exc, APIException)
        assert hasattr(
            exc, "default_detail"
        ), f"{exc} has no 'default_detail' attribute"
        db_err.description_for_devs = str(exc.default_detail)
        db_err.description_for_users = str(exc.detail)
        serialized_error = ErrorSerializer(db_err).data
        return Response(serialized_error, status=response.status_code)

    db_err.save()

    serialized_error = ErrorSerializer(db_err).data
    status = str(exc.status_code) if hasattr(exc, "status_code") else 500  # type: ignore  # noqa: PGH003
    return Response(serialized_error, status=status)  # type: ignore  # noqa: PGH003
