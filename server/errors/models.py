from django.db import models
from django.utils import timezone
from rest_framework import serializers
from rest_framework.response import Response

from errors.codes import status_code_mapping


class Error(models.Model):
    # Fields to be sent to the client
    error_code = models.IntegerField(
        verbose_name="Код ошибки",
        default=400,
    )
    description_for_devs = models.TextField(
        verbose_name="Техническое описание ошибки для разработчиков",
    )
    description_for_users = models.TextField(
        verbose_name="Описание для UI",
        help_text="Можно показывать пользователю в диалоговом окне для ошибок",
        default="",
    )
    # Fields to keep on server
    stacktrace = models.TextField(
        verbose_name="Stacktrace",
        default="",
        blank=True,
    )
    created_date = models.DateTimeField(
        verbose_name="Время ошибки",
        default=timezone.now,
        editable=False,
    )
    handled_gracefully = models.BooleanField(
        verbose_name="Была ли ошибка обработана кодом (или поймана exception handler middleware'ом)",
        default=True,
    )

    class Meta:
        verbose_name = "Ошибка"
        verbose_name_plural = "Ошибки"

    def __str__(self) -> str:
        return f"{self.pk}:{self.description_for_devs}"

    def serialize_response(self) -> Response:
        return Response(
            GracefulErrorSerializer(instance=self).data,
            status=status_code_mapping.get(self.error_code, 418),
        )


class GracefulErrorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Error
        fields = (
            "error_code",
            "description_for_devs",
            "description_for_users",
        )
