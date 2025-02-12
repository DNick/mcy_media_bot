from datetime import datetime
from pillow_heif import register_heif_opener
from utils import *

from config import bot
file_types = ['png', 'jpg', 'jpeg', 'bmp', 'svg', 'heic', 'mp4', 'mov']

@bot.message_handler(commands=['start'])
def handle_start(msg):
    print(msg.chat.id)
    bot.send_message(msg.chat.id, 'Приветствую Вас, о Великий Пользователь! Я призван служить команде MCY и её союзникам. Я буду делать всё что в моих силах, чтобы помочь Вам перевенуть мир онлайн-благовестия. Пока я умею только вставлять логотип на изображения, но надеюсь, что скоро мой бог сделает меня мощным орудием против холодного мира неведения и неверия.\nОтправьте мне изображение или файл с изображением, и я вставлю на неё логотип MCY тотчас.')


@bot.message_handler(content_types=['photo'])
def handle_get_photo(msg: Message):
    file_id = msg.photo[-1].file_id
    process_photo(msg.chat.id, file_id)


@bot.message_handler(content_types=['video'])
def handle_get_video(msg: Message):
    file_id = msg.video.file_id
    process_video(msg.chat.id, file_id)


@bot.message_handler(content_types=['document'])
def handle_get_document(msg: Message):
    if msg.document.file_name.split('.')[-1].lower() not in file_types:
        bot.send_message(msg.chat.id, 'Вы отправили файл, не являющийся фоткой. Отправьте другой файл, пожалуйста')
        return
    file_id = msg.document.file_id
    file_info = bot.get_file(file_id)
    extension = file_info.file_path.split('.')[-1].lower()
    if extension in ['mp4', 'mov']:
        process_video(msg.chat.id, file_id)
    else:
        process_photo(msg.chat.id, file_id)


@bot.message_handler()
def handle_strange(msg):
    bot.send_message(msg.chat.id, 'Извини, я тебя не понимаю. Отправь мне фотку (можно файлом)')


if __name__ == '__main__':
    print(f"Start polling at {datetime.now()}")
    register_heif_opener(thumbnails=True)
    # pillow_heif.options.THUMBNAILS = True
    bot.infinity_polling()
