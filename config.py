"""Конфигурация бота и общий экземпляр TeleBot."""

import html
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
    alert_group_id: int
    telegram_proxy: str | None = None


SETTINGS = Settings()

if SETTINGS.telegram_proxy:
    apihelper.proxy = {"https": SETTINGS.telegram_proxy}


class AlertExceptionHandler(ExceptionHandler):
    """Логирует необработанные ошибки и шлёт их в группу разработчиков."""

    def handle(self, exception: Exception) -> bool:
        logger.exception("Необработанная ошибка в боте")
        body = html.escape(str(exception))
        BOT.send_message(
            SETTINGS.alert_group_id,
            f'Ошибка в боте:\n<pre><code class="language-error">{body}</code></pre>',
            parse_mode="HTML",
        )
        return True


BOT = TeleBot(SETTINGS.bot_token, exception_handler=AlertExceptionHandler())
