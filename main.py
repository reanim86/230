import requests
import psycopg
from pprint import pprint
from datetime import date, timedelta, datetime
import configparser
from telegram import send_mes_telebot, send_file_telebot
import csv

def get_data(sms_login, sms_pass): # Очистить скобки
    """
    Запрос истории отправко смс за вчерашний день
    :return: список с смс
    """
    yesterday = date.today() - timedelta(days=1)
    params = {
                'get_messages': 1,
                'login': sms_login, # Заменить в ВДМ
                'psw': sms_pass, # Заменить в ВДМ
                # 'start': '25.01.2025', # раскоментить в ВДМ
                # 'end': '25.01.2025', # раскоментить в ВДМ
                'start': yesterday.strftime('%d.%m.%Y'), #  В ВДМ строку заккоментировать
                'end': yesterday.strftime('%d.%m.%Y'), #  В ВДМ строку заккоментировать
                'cnt': 1000,
                'fmt': 3
            }
    response = requests.get('https://smsc.ru/sys/get.php', params=params)
    return response.json()

def create_record(message):
    """
    Создание записей в БД
    :param message: список отправленных смс
    """
    for sms in message:
        date = datetime.strptime(sms['send_date'], '%d.%m.%Y %H:%M:%S') # В ВДМ строку закомментировать
        with conn.cursor() as cur:
            cur.execute("""
            INSERT INTO sms(id_smsc, date_create, tel, mccmnc, operator, description, name_sender, quantity, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);
            """, (sms['id'], date.strftime('%m.%d.%Y %H:%M:%S'), sms['phone'], sms['mccmnc'], sms['operator'],
                  sms['message'], sms['sender_id'], sms['sms_cnt'], sms['status_name'])) # Изменить поле даты
    return

def count_record():
    """
    Провевряем количество записей в таблице БД
    :return: количество записей
    """
    with conn.cursor() as cur:
        cur.execute("""
        SELECT COUNT(*) FROM sms;
        """)
        return cur.fetchone()[0]

def create_csv(messages):
    """
    Формируем csv из которого отправляют смс
    :param messages: полный перечень смс
    :return: урезанный перечень
    """
    messages_list = []
    for message in messages:
        message_dict = {}
        message_dict['Дата'] = message['send_date']
        message_dict['Телефон'] = message['phone']
        message_dict['sms'] = message['message']
        messages_list.append(message_dict)
    keys = messages_list[0].keys()
    with open(f'C://reestr/{date.today() - timedelta(days=1)}.csv', 'w', newline='') as output_file:
        dict_writer = csv.DictWriter(output_file, keys)
        dict_writer.writeheader()
        dict_writer.writerows(messages_list)
    return

def undelivered_message(messages):
    """
    Формируем список недоствленных сообщений
    :param messages: список всех сообщений
    :return: путь к файлу с недоставленными смс
    """
    messages_list = []
    for message in messages:
        if message['status_name'] != 'Доставлено':
            messages_list.append(message)
    if not messages_list:
        return 'нет недоставленных сообщений'
    keys = messages_list[0].keys()
    bad_messages_list = []
    for message in messages_list:
        if keys != message.keys():    # Проверка совпадения ключей в ответе от smsc
            keys_one = set(message.keys()) # Преобразуем ключи в set
            keys_two = set(keys)
            same_keys = keys_one.difference(keys_two) # Выявляем лишний ключ
            if len(same_keys) == 0: # Если его нет, то добавляем ключ которого нет с нулевым значением
                keys_same = keys_two.difference(keys_one)  # Смотрим разницу исходя из другого вводного условия какой набор ключей явялется заголовком csv файла
                for bad_key in keys_same: # Перебор на случай если лишних ключей больше одного и их удаление
                    message[bad_key] = 0
            else:
                for bad_key in same_keys: # Перебор на случай если лишних ключей больше одного и их удаление
                    del message[bad_key]
            bad_messages_list.append(message)
        else:
            bad_messages_list.append(message)
    with open(f'C://reestr/undelivered/{org}_{date.today() - timedelta(days=1)}.csv', 'w', newline='') as output_file:
        dict_writer = csv.DictWriter(output_file, keys)
        dict_writer.writeheader()
        dict_writer.writerows(bad_messages_list)
    return f'C://reestr/undelivered/{org}_{date.today() - timedelta(days=1)}.csv'




if __name__ == '__main__':
    config = configparser.ConfigParser() #  В ВДМ строку заккоментировать
    config.read('settings.ini') #  В ВДМ строку заккоментировать
    login = config['sms']['login'] #  В ВДМ строку заккоментировать
    password = config['sms']['pass'] #  В ВДМ строку заккоментировать
    data = get_data(login, password) # Убрать данные
    chat_id = '-1002637340041'
    chat_bad_sms = '-4671413664'
    org = 'ВДМ'  # Исправить организацию
    if type(data) is dict: # Проверка были ли вообще отправленные сообщения, если были сообщения то вернется список
        if data['error_code'] == 3:
            text = f'По организации {org} за {date.today() - timedelta(days=1)} сообщений не было'
            send_mes_telebot(text, chat_id)
            send_mes_telebot(text, chat_bad_sms)
        else:
            text = f'По организации {org} ошибка: {data}, см. описание ошибок на сайте smsc.ru в разделе API'
            send_mes_telebot(text, chat_id)
            send_mes_telebot(text, chat_bad_sms)
    else:
        with psycopg.connect(dbname='sms', user='postgres', password='postgres') as conn:
            count_before = count_record()
            create_record(data)
            count_after = count_record()
        conn.close()
        create_csv(data)
        text = f'Файл для отправки смс {org} создан'
        send_mes_telebot(text, chat_id)
        count_added = count_after - count_before
        text = f'По МКК {org} добавлено {count_added} строк'
        send_mes_telebot(text, chat_id)
        bad_csv = undelivered_message(data)
        if bad_csv == 'нет недоставленных сообщений':
            text = f'По организации {org} ' + bad_csv
            send_mes_telebot(text, chat_bad_sms)
        else:
            send_file_telebot(bad_csv, chat_bad_sms)



