from typing import TYPE_CHECKING

from django.utils import timezone

from errors import codes

if TYPE_CHECKING:
    from datetime import datetime


class MailerError(Exception):
    # TODO: добавить "save_to_db"?
    def __init__(
        # TODO: подумать, как пофиксить ruff-ошибки
        self,
        description_for_devs: str = "Unknown error",
        # TODO: переименовать в code
        error_code: int = codes.unhandled_error,
        description_for_users: str = "На сервере произошла внутренняя ошибка. Обратитесь в службу поддержки.",
        stacktrace: str | None = None,
        handled_gracefully: bool = True,
    ) -> None:
        self.error_code = error_code
        self.description_for_devs = description_for_devs
        self.description_for_users: str = description_for_users
        self.stacktrace = stacktrace
        self.handled_gracefully = handled_gracefully
        self.created_date: datetime = timezone.now()

        super().__init__(self.description_for_devs)

    def __str__(self) -> str:
        return self.description_for_devs
