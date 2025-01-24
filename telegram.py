import configparser
import telebot

def send_mes_telebot(messege, chat):
    """
    Отправка файла в телеграм с помощь. бота
    :param messege: количество строк в таблице БД
    :param chat: id чата
    """
    bot = telebot.TeleBot(token)
    bot.send_message(chat, messege)
    return

def send_file_telebot(file, chat):
    """
    Отправка файла в телеграм с помощь. бота
    :param file: путь к файлу
    :param chat: id чата
    """
    bot = telebot.TeleBot(token)
    f = open(file, "rb")
    bot.send_document(chat, f)
    return

config = configparser.ConfigParser()
config.read('settings.ini')
token = config['Tg']['token'] #Прописать токен