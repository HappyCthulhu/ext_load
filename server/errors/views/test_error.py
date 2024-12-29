from django.db.models import TextChoices
from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework.decorators import api_view, permission_classes
from rest_framework.exceptions import (
    NotAuthenticated,
    PermissionDenied,
    ValidationError,
)
from rest_framework.permissions import IsAdminUser
from rest_framework.request import Request
from rest_framework.response import Response

from errors import codes
from errors.error import MailerError


class ErrorEnum(TextChoices):
    validation = "ValidationError", _("Ошибка валидации")
    value_er = "ValueError", _("Значение не найдено")
    key = "KeyError", _("Ключ не найден")
    mailer = "Mailer", _("Ошибка внутри мейлера")
    not_authenticated = "NotAuthenticated", _("Не аутентифицирован")
    permission_denied = "PermissionDenied", _("Доступ запрещен")
    assertion_error = "AssertionError", _("AssertionError")


@extend_schema(
    summary="Test different error types",
    parameters=[
        OpenApiParameter(
            name="error_type",
            type=str,
            required=True,
            enum=[
                ErrorEnum.validation.value,
                ErrorEnum.value_er.value,
                ErrorEnum.key.value,
                ErrorEnum.mailer.value,
                ErrorEnum.not_authenticated.value,
                ErrorEnum.permission_denied.value,
                ErrorEnum.assertion_error.value,
            ],
        ),
    ],
    responses={
        "200": None,
    },
)
@permission_classes([IsAdminUser])
@api_view(["GET"])
def return_error(request: Request) -> Response:
    match request.query_params["error_type"]:
        case ErrorEnum.key.value:
            raise KeyError(ErrorEnum.key.label)
        case ErrorEnum.value_er.value:
            raise ValueError(ErrorEnum.value_er.label)
        case ErrorEnum.validation.value:
            raise ValidationError(ErrorEnum.validation.label)
        case ErrorEnum.not_authenticated.value:
            raise NotAuthenticated(ErrorEnum.not_authenticated.label)
        case ErrorEnum.permission_denied.value:
            raise PermissionDenied(ErrorEnum.permission_denied.label)
        case ErrorEnum.assertion_error.value:
            raise AssertionError(ErrorEnum.assertion_error.label)
        case ErrorEnum.mailer.value:
            trace = "Mailer error happend"
            raise MailerError(
                trace,
                error_code=codes.invalid_request_data,
                description_for_users="Произошла ошибка внутри мейлера",
                handled_gracefully=True,
            )

    return Response("No error was raised")
