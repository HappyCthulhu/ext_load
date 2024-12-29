from rest_framework.mixins import ListModelMixin  # noqa: INP001
from rest_framework.viewsets import GenericViewSet

from errors.models import Error
from errors.serializers import ErrorSerializer


class ErrorViewSet(GenericViewSet, ListModelMixin):
    queryset = Error.objects.order_by("-created_date").all()[:1000]
    serializer_class = ErrorSerializer
