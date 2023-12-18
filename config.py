from telebot import TeleBot, ExceptionHandler
from dotenv import dotenv_values

values = dotenv_values()


class MyExceptionHandler(ExceptionHandler):
    def handle(self, exception):
        print(str(exception))
        bot.send_message(values['MAINTAINER_CHAT_ID'], f'Ошибка в боте:\n\n{str(exception)}')
        return True


bot = TeleBot(values['BOT_TOKEN'], exception_handler=ExceptionHandler())
