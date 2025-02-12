from config import bot
from datetime import datetime
from io import BytesIO
from pillow_heif import HeifImagePlugin
from telebot.types import Message
from PIL import Image, ImageFilter, ImageEnhance
import moviepy.editor as mp
import ffmpeg


def get_video_resolution():
    probe = ffmpeg.probe('video1.mp4')
    video_stream = next((stream for stream in probe['streams'] if stream['codec_type'] == 'video'), None)
    if video_stream:
        width = video_stream['width']
        height = video_stream['height']
        return width, height


def process_video(chat_id, file_id):
    file_info = bot.get_file(file_id)

    downloaded_file = bot.download_file(file_info.file_path)

    # bio = BytesIO(downloaded_file)
    # bio.name = save_path
    # bio.seek(0)
    # with open("output.mp4", "wb") as f:
    #     f.write(bio.getbuffer())

    # Сохраняем файл локально
    with open('video1.mp4', "wb") as file:
        file.write(downloaded_file)

    width, height = get_video_resolution()
    logo = Image.open('logo.png')
    # positions = {
    #     "top_left": ("10", "10"),
    #     "top_right": ("main_w-overlay_w-10", "10"),
    #     "bottom_left": ("10", "main_h-overlay_h-10"),
    #     "bottom_right": ("main_w-overlay_w-10", "main_h-overlay_h-10")
    # }
    #
    # x, y = positions.get(position, ("main_w-overlay_w-10", "10"))  # Координаты логотипа
    logo, point = get_resized_logo_and_point(logo, height, width)
    logo.save('logo_resized.png')
    # Загружаем видео
    video = ffmpeg.input('video1.mp4')
    # Улучшаем чёткость
    enhanced_video = (
        video
        # .filter("unsharp", luma_msize_x=5, luma_msize_y=5, luma_amount=1.5)
        .filter("hqdn3d", 1.5, 1.5, 6, 6)
    )
    # enhanced_video = enhanced_video.filter("transpose", 0)
    # Извлекаем аудио
    audio = ffmpeg.input('video1.mp4').audio  # Загружаем аудио отдельно

    # Загружаем логотип и масштабируем
    logo = (
        ffmpeg
        .input('logo_resized.png')
        # .filter("scale", 100, -1)
    )

    # Накладываем логотип на видео
    video_with_logo = (
        ffmpeg
        .overlay(enhanced_video, logo, x="main_w-overlay_w-10", y="main_h-overlay_h-10")
    )

    # Объединяем видео с логотипом + аудио
    output = (
        ffmpeg
        .output(video_with_logo, audio, 'video.mp4', vcodec="libx264", acodec="aac", strict="experimental",
                codec="copy")
    )

    # Запускаем обработку
    output.run(overwrite_output=True)

    with open('video.mp4', 'rb') as file:
        bot.send_document(chat_id, file)

    # photo = Image.open(bio)
    #
    # logo = Image.open('logo.png')
    #
    # if photo.height > photo.width:
    #     ratio = 1 / 23
    # else:
    #     ratio = 1 / 16
    #
    # logo = logo.resize((int((photo.height * ratio) / logo.height * logo.width), int(photo.height * ratio)))
    # point = (photo.width - logo.width - photo.width // 90, photo.height - logo.height - photo.height // 90)
    # photo.paste(logo, point, mask=logo) # добавляет png фотку с прозрачным фоном
    #
    # photo = ImageEnhance.Color(photo).enhance(1.17).filter(ImageFilter.SHARPEN) # делаю более чётким и насыщенным
    # bot.send_message(msg.chat.id, 'Готово!')
    #
    # photo.save(save_path, quality=95)
    #
    # bot.send_document(msg.chat.id, open(save_path, 'rb'))


def process_photo(chat_id, file_id):
    file_info = bot.get_file(file_id)
    extension = file_info.file_path.split('.')[-1].lower()

    if extension == 'heic': extension = 'jpg'
    downloaded_file = bot.download_file(file_info.file_path)
    save_path = 'picture.' + extension

    bio = BytesIO(downloaded_file)
    bio.name = save_path
    bio.seek(0)

    photo = Image.open(bio)

    logo = Image.open('logo.png')
    logo, point = get_resized_logo_and_point(logo, photo.height, photo.width)

    photo.paste(logo, point, mask=logo)  # добавляет png фотку с прозрачным фоном

    photo = ImageEnhance.Color(photo).enhance(1.17).filter(ImageFilter.SHARPEN)  # делаю более чётким и насыщенным
    bot.send_message(chat_id, 'Готово!')

    photo.save(save_path, quality=95)

    bot.send_document(chat_id, open(save_path, 'rb'))

    # bot.send_photo(msg.chat.id, photo)


def get_resized_logo_and_point(logo, height, width):
    if height > width:
        ratio = 1 / 23
    else:
        ratio = 1 / 16
    new_logo = logo.resize((int((height * ratio) / logo.height * logo.width), int(height * ratio)))
    point = (width - logo.width - width // 90, height - logo.height - height // 90)
    return new_logo, point





# if msg.document:
#     if msg.document.file_name.split('.')[-1].lower() not in file_types:
#         bot.send_message(msg.chat.id, 'Вы отправили файл, не являющийся фоткой. Отправьте другой файл, пожалуйста')
#         return
#     file_id = msg.document.file_id
#     # size = (msg.document.thumbnail.width, msg.document.thumbnail.height)
# else:
#     file_id = msg.photo[-1].file_id
#     # size = (msg.photo[-1].width, msg.photo[-1].height)
#
# file_info = bot.get_file(file_id)
# extension = file_info.file_path.split('.')[-1].lower()
#
# if extension == 'heic': extension = 'jpg'
# downloaded_file = bot.download_file(file_info.file_path)
# save_path = 'picture.' + extension
# # with open(save_path, 'wb') as new_file:
# #     new_file.write(downloaded_file)
#
# bio = BytesIO(downloaded_file)
# bio.name = save_path
# bio.seek(0)
#
# # photo = Image.open(save_path)
#
# photo = Image.open(bio)
#
# logo = Image.open('logo.png')
#
# if photo.height > photo.width:
#     ratio = 1 / 23
# else:
#     ratio = 1 / 16
# # coordinates = (int(1357 / 1432 * photo.width), int(947 / 1080 * photo.height))
# logo = logo.resize((int((photo.height * ratio) / logo.height * logo.width), int(photo.height * ratio)))
# point = (photo.width - logo.width - photo.width // 90, photo.height - logo.height - photo.height // 90)
# photo.paste(logo, point, mask=logo) # добавляет png фотку с прозрачным фоном
#
# photo = ImageEnhance.Color(photo).enhance(1.17).filter(ImageFilter.SHARPEN) # делаю более чётким и насыщенным
# bot.send_message(msg.chat.id, 'Готово!')
#
# photo.save(save_path, quality=95)
#
# # bio = BytesIO()
# # bio.name = save_path
# # photo.save(bio, extension)
# # bio.seek(0)
# # bot.send_document(msg.chat.id, bio)
#
# bot.send_document(msg.chat.id, open(save_path, 'rb'))
#
# # bot.send_photo(msg.chat.id, photo)