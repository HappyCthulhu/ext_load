from django.contrib import admin

from errors.models import Error


@admin.register(Error)
class ErrorAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "description_for_devs",
        "description_for_users",
        "stacktrace",
        "created_date",
        "handled_gracefully",
        "error_code",
    )
