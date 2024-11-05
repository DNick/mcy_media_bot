from datetime import datetime
from io import BytesIO
# from pillow_heif import register_heif_opener
from pillow_heif import HeifImagePlugin
from telebot.types import Message
from PIL import Image, ImageFilter, ImageEnhance
# import tensorflow as tf
# import tensorflow_hub as hub
# import numpy as np
# import pillow_heif


from config import bot
file_types = ['png', 'jpg', 'jpeg', 'bmp', 'svg', 'heic']

@bot.message_handler(commands=['start'])
def handle_start(msg):
    print(msg.chat.id)
    bot.send_message(msg.chat.id, 'Приветствую Вас, о Великий Пользователь! Я призван служить команде MCY и её союзникам. Я буду делать всё что в моих силах, чтобы помочь Вам перевенуть мир онлайн-благовестия. Пока я умею только вставлять логотип на изображения, но надеюсь, что скоро мой бог сделает меня мощным орудием против холодного мира неведения и неверия.\nОтправьте мне изображение или файл с изображением, и я вставлю на неё логотип MCY тотчас.')


@bot.message_handler(content_types=['document', 'photo'])
def handle_get_photo(msg: Message):
    if msg.document:
        if msg.document.file_name.split('.')[-1].lower() not in file_types:
            bot.send_message(msg.chat.id, 'Вы отправили файл, не являющийся фоткой. Отправьте другой файл, пожалуйста')
            return
        file_id = msg.document.file_id
        # size = (msg.document.thumbnail.width, msg.document.thumbnail.height)
    else:
        file_id = msg.photo[-1].file_id
        # size = (msg.photo[-1].width, msg.photo[-1].height)

    file_info = bot.get_file(file_id)
    extension = file_info.file_path.split('.')[-1].lower()
    if extension == 'heic': extension = 'jpg'
    downloaded_file = bot.download_file(file_info.file_path)
    save_path = 'picture.' + extension
    # with open(save_path, 'wb') as new_file:
    #     new_file.write(downloaded_file)

    bio = BytesIO(downloaded_file)
    bio.name = save_path
    bio.seek(0)

    # photo = Image.open(save_path)

    photo = Image.open(bio)

    logo = Image.open('logo.png')

    if photo.height > photo.width:
        ratio = 1 / 23
    else:
        ratio = 1 / 16
    # coordinates = (int(1357 / 1432 * photo.width), int(947 / 1080 * photo.height))
    logo = logo.resize((int((photo.height * ratio) / logo.height * logo.width), int(photo.height * ratio)))
    point = (photo.width - logo.width - photo.width // 90, photo.height - logo.height - photo.height // 90)
    photo.paste(logo, point, mask=logo) # добавляет png фотку с прозрачным фоном

    photo = ImageEnhance.Color(photo).enhance(1.17).filter(ImageFilter.SHARPEN) # делаю более чётким и насыщенным
    bot.send_message(msg.chat.id, 'Готово!')

    photo.save(save_path, quality=95)

    # bio = BytesIO()
    # bio.name = save_path
    # photo.save(bio, extension)
    # bio.seek(0)
    # bot.send_document(msg.chat.id, bio)

    bot.send_document(msg.chat.id, open(save_path, 'rb'))

    # bot.send_photo(msg.chat.id, photo)


@bot.message_handler()
def handle_strange(msg):
    bot.send_message(msg.chat.id, 'Извини, я тебя не понимаю. Отправь мне фотку (можно файлом)')


if __name__ == '__main__':
    print(f"Start polling at {datetime.now()}")
    # register_heif_opener(thumbnails=True)
    # pillow_heif.options.THUMBNAILS = True
    bot.infinity_polling()
