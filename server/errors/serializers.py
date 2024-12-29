from typing import ClassVar

from rest_framework import serializers

from errors.models import Error


class ErrorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Error
        fields = (
            "error_code",
            "description_for_devs",
            "description_for_users",
            "stacktrace",
        )
        extra_kwargs: ClassVar[dict[str, dict[str, bool]]] = {
            "stacktrace": {"write_only": True},
            "created_date": {"write_only": True},
            "handled_gracefully": {"write_only": True},
        }
