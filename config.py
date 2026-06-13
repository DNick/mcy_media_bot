"""Конфигурация бота и общий экземпляр TeleBot."""

from __future__ import annotations

import logging

from pydantic_settings import BaseSettings, SettingsConfigDict
from telebot import ExceptionHandler, TeleBot

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    """Настройки приложения.

    Значения подхватываются автоматически при создании объекта: из переменных
    окружения (Docker/Portainer) и из файла .env (локально) — без load_dotenv().
    """

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    bot_token: str
    maintainer_chat_id: int


settings = Settings()


class MaintainerExceptionHandler(ExceptionHandler):
    """Логирует необработанные ошибки и пересылает их мейнтейнеру в чат."""

    def handle(self, exception: Exception) -> bool:
        logger.exception("Необработанная ошибка в боте")
        bot.send_message(settings.maintainer_chat_id, f"Ошибка в боте:\n\n{exception}")
        return True


bot = TeleBot(settings.bot_token, exception_handler=MaintainerExceptionHandler())
