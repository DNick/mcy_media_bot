"""Telegram-бот, накладывающий логотип MCY на фото и видео."""

import logging
from collections.abc import Callable

from pillow_heif import register_heif_opener
from telebot.types import Message

from config import BOT, SETTINGS
from media import process_photo, process_video

logger = logging.getLogger(__name__)

# Расширения, принимаемые при отправке изображения/видео файлом.
SUPPORTED_FILE_TYPES = ("png", "jpg", "jpeg", "bmp", "svg", "heic", "mp4", "mov")
VIDEO_FILE_TYPES = ("mp4", "mov")

START_MESSAGE = (
    "Приветствую Вас, о Великий Пользователь! Я призван служить команде MCY и её "
    "союзникам. Я буду делать всё что в моих силах, чтобы помочь Вам перевенуть мир "
    "онлайн-благовестия. Пока я умею только вставлять логотип на изображения, но "
    "надеюсь, что скоро мой бог сделает меня мощным орудием против холодного мира "
    "неведения и неверия.\nОтправьте мне изображение или файл с изображением, и я "
    "вставлю на неё логотип MCY тотчас."
)


def _run(chat_id: int, processor: Callable[[int, str], None], file_id: str) -> None:
    """Показывает индикацию обработки и сообщает пользователю, если что-то пошло не так."""
    try:
        BOT.send_chat_action(chat_id, "upload_document")
        processor(chat_id, file_id)
    except Exception:
        BOT.send_message(chat_id, "Не удалось обработать файл. Попробуйте прислать другой.")
        raise  # пробрасываем дальше — сработает AlertExceptionHandler


@BOT.message_handler(commands=["start"])
def handle_start(msg: Message) -> None:
    logger.info("Новый чат: %s", msg.chat.id)
    BOT.send_message(msg.chat.id, START_MESSAGE)


@BOT.message_handler(content_types=["photo"])
def handle_photo(msg: Message) -> None:
    _run(msg.chat.id, process_photo, msg.photo[-1].file_id)


@BOT.message_handler(content_types=["video"])
def handle_video(msg: Message) -> None:
    _run(msg.chat.id, process_video, msg.video.file_id)


@BOT.message_handler(content_types=["document"])
def handle_document(msg: Message) -> None:
    if msg.document.file_name.split(".")[-1].lower() not in SUPPORTED_FILE_TYPES:
        BOT.send_message(
            msg.chat.id,
            "Вы отправили файл, не являющийся фоткой. Отправьте другой файл, пожалуйста",
        )
        return

    file_info = BOT.get_file(msg.document.file_id)
    extension = file_info.file_path.split(".")[-1].lower()
    processor = process_video if extension in VIDEO_FILE_TYPES else process_photo
    _run(msg.chat.id, processor, msg.document.file_id)


@BOT.message_handler()
def handle_unknown(msg: Message) -> None:
    BOT.send_message(msg.chat.id, "Извини, я тебя не понимаю. Отправь мне фотку (можно файлом)")


def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    if SETTINGS.telegram_proxy:
        logger.info("Telegram API через прокси: %s", SETTINGS.telegram_proxy)
    logger.info("Запуск polling")
    register_heif_opener(thumbnails=True)
    BOT.infinity_polling()


if __name__ == "__main__":
    main()
