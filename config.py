"""Конфигурация бота и общий экземпляр TeleBot."""

import logging

from pydantic_settings import BaseSettings, SettingsConfigDict
from telebot import ExceptionHandler, TeleBot, apihelper

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    """Настройки приложения.

    Значения подхватываются автоматически при создании объекта: из переменных
    окружения (Docker/Portainer) и из файла .env (локально) — без load_dotenv().
    """

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    bot_token: str
    maintainer_chat_id: int
    telegram_proxy: str | None = None


SETTINGS = Settings()

if SETTINGS.telegram_proxy:
    apihelper.proxy = {"https": SETTINGS.telegram_proxy}


class MaintainerExceptionHandler(ExceptionHandler):
    """Логирует необработанные ошибки и пересылает их мейнтейнеру в чат."""

    def handle(self, exception: Exception) -> bool:
        logger.exception("Необработанная ошибка в боте")
        BOT.send_message(SETTINGS.maintainer_chat_id, f"Ошибка в боте:\n\n{exception}")
        return True


BOT = TeleBot(SETTINGS.bot_token, exception_handler=MaintainerExceptionHandler())
