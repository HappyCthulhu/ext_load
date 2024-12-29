from django.urls import path
from rest_framework.routers import SimpleRouter

from errors.views.error import ErrorViewSet
from errors.views.test_error import return_error

router = SimpleRouter()

router.register("error", ErrorViewSet, basename="errors")
urlpatterns = [
    path("testerror/", return_error),
    *router.urls,
]
