import logging
from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

from app.config import Config

logger = logging.getLogger(__name__)


class ConfigMiddleware(BaseMiddleware):
    """
    Middleware for injecting a Config instance into handler data.

    This middleware injects a `Config` instance into the handler's data dictionary, making
    configuration settings accessible in every handler.
    """

    def __init__(self, config: Config) -> None:
        """
        Initializes the ConfigMiddleware with a Config instance.

        Arguments:
            config (Config): The `Config` instance that will be injected into handler data.
        """
        self.config = config

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        """
        Middleware handler to inject the config into handler data.

        Arguments:
            handler (Callable): The handler function to process the event.
            event (TelegramObject): The incoming Telegram event.
            data (dict): Context data passed to the handler.

        Returns:
            Any: The result of the next handler with injected config.
        """
        data["config"] = self.config
        return await handler(event, data)
