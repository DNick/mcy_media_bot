from datetime import datetime
from telebot.types import Message
from PIL import Image

# sys.path.append('/root/ivr/')
from config import bot


@bot.message_handler(commands=['start'])
def handle_start(msg):
    bot.send_message(msg.chat.id, 'Приветствую Вас, о Великий Пользователь! Я призван служить команде MCY и её союзникам. Я буду делать всё что в моих силах, чтобы помочь Вам перевенуть мир онлайн-благовестия. Пока я умею только вставлять логотип на фотки, но надеюсь, что скоро мой бог сделает меня мощным орудием против холодного мира неведения и неверия.\nОтправьте мне фотку, и я вставлю на неё логотип MCY тотчас.')


@bot.message_handler(content_types=['document', 'photo'])
def handle_get_photo(msg: Message):
    photo = msg.photo[-1]
    file_info = bot.get_file(photo.file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    save_path = 'current_picture.jpg'
    with open(save_path, 'wb') as new_file:
        new_file.write(downloaded_file)

    photo = Image.open(save_path)

    logo = Image.open('logo.png')
    ratio = 0.35
    logo = logo.resize((int(logo.width * ratio), int(logo.height * ratio)))

    point = (photo.width - logo.width - 17, photo.height - logo.height - 11)
    photo.paste(logo, point, mask=logo)
    bot.send_message(msg.chat.id, 'Готово, Господин')
    bot.send_photo(msg.chat.id, photo)


@bot.message_handler()
def handle_strange(msg):
    bot.send_message(msg.chat.id, 'Извини, я тебя не понимаю. Отправь мне фотку (можно файлом)')


if __name__ == '__main__':
    print(f"Start polling at {datetime.now()}")
    bot.infinity_polling()