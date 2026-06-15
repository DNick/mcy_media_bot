"""Обработка медиа: наложение логотипа MCY на фото и видео."""

import tempfile
from io import BytesIO
from pathlib import Path

import ffmpeg
from PIL import Image, ImageEnhance, ImageFilter, ImageOps

from config import BOT

_BASE_DIR = Path(__file__).resolve().parent
LOGO_PATH = _BASE_DIR / "logo.png"


def get_resized_logo_and_point(
    logo: Image.Image, height: int, width: int
) -> tuple[Image.Image, tuple[int, int]]:
    """Масштабирует логотип под кадр и возвращает его позицию в правом нижнем углу."""
    ratio = 1 / 27 if height > width else 1 / 16
    new_logo = logo.resize((int((height * ratio) / logo.height * logo.width), int(height * ratio)))
    point = (
        width - new_logo.width - width // 90,
        height - new_logo.height - height // 90,
    )
    return new_logo, point


def get_video_resolution(path: str) -> tuple[int, int]:
    """Возвращает (ширина, высота) первого видеопотока файла."""
    probe = ffmpeg.probe(path)
    video_stream = next(
        (stream for stream in probe["streams"] if stream["codec_type"] == "video"), None
    )
    if video_stream is None:
        raise ValueError("В файле нет видеопотока")
    return video_stream["width"], video_stream["height"]


def process_photo(chat_id: int, file_id: str) -> None:
    file_info = BOT.get_file(file_id)
    extension = file_info.file_path.split(".")[-1].lower()
    if extension == "heic":
        extension = "jpg"

    downloaded_file = BOT.download_file(file_info.file_path)

    photo = Image.open(BytesIO(downloaded_file))
    photo = ImageOps.exif_transpose(photo)  # учитываем ориентацию из EXIF (фото с телефонов)

    logo = Image.open(LOGO_PATH)
    logo, point = get_resized_logo_and_point(logo, photo.height, photo.width)
    photo.paste(logo, point, mask=logo)  # добавляет PNG с прозрачным фоном

    # делаю изображение более чётким и насыщенным
    photo = ImageEnhance.Color(photo).enhance(1.17).filter(ImageFilter.SHARPEN)

    with tempfile.TemporaryDirectory() as tmp:
        save_path = Path(tmp) / f"picture.{extension}"
        photo.save(save_path, quality=95)
        with open(save_path, "rb") as result:
            BOT.send_document(chat_id, result)

    BOT.send_message(chat_id, "Готово!")


def process_video(chat_id: int, file_id: str) -> None:
    file_info = BOT.get_file(file_id)
    downloaded_file = BOT.download_file(file_info.file_path)

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        source = tmp_path / "source.mp4"
        resized_logo = tmp_path / "logo.png"
        output = tmp_path / "output.mp4"

        source.write_bytes(downloaded_file)

        width, height = get_video_resolution(str(source))
        logo = Image.open(LOGO_PATH)
        logo, _ = get_resized_logo_and_point(logo, height, width)
        logo.save(resized_logo)

        video = ffmpeg.input(str(source))
        enhanced_video = video.filter("hqdn3d", 1.5, 1.5, 6, 6)  # шумоподавление
        audio = ffmpeg.input(str(source)).audio
        logo_input = ffmpeg.input(str(resized_logo))

        video_with_logo = ffmpeg.overlay(
            enhanced_video, logo_input, x="main_w-overlay_w-10", y="main_h-overlay_h-10"
        )
        output_stream = ffmpeg.output(
            video_with_logo,
            audio,
            str(output),
            vcodec="libx264",
            acodec="aac",
            strict="experimental",
            codec="copy",
        )
        output_stream.run(overwrite_output=True)

        with open(output, "rb") as result:
            BOT.send_document(chat_id, result)

    BOT.send_message(chat_id, "Готово!")
