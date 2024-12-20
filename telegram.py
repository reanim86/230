import configparser
import telebot

def send_mes_telebot(messege, chat):
    """
    Отправка файла в телеграм с помощь. бота
    :param messege: количество строк в таблице БД
    :param chat: id чата
    """
    bot = telebot.TeleBot(token)
    text = f'По МКК ВДМ добалвено {messege} строк'
    bot.send_message(chat, text)
    return

config = configparser.ConfigParser()
config.read('settings.ini')
token = config['Tg']['token']