import requests
import csv


def get_data():
    """
    Запрос истории отправко смс за вчерашний день
    :return: список с смс
    """
    params = {
                'get_messages': 1,
                'login': 'vdm',
                'psw': 'UtyidzoyHicsi2I',
                'start': '11.12.2024',
                'end': '11.12.2024',
                'cnt': 1000,
                'fmt': 3
            }
    response = requests.get('https://smsc.ru/sys/get.php', params=params)
    return response.json()