import requests
import psycopg
from pprint import pprint
from datetime import date, timedelta, datetime
import configparser

def get_data(sms_login, sms_pass):
    """
    Запрос истории отправко смс за вчерашний день
    :return: список с смс
    """
    yesterday = date.today() - timedelta(days=1)
    params = {
                'get_messages': 1,
                'login': sms_login,
                'psw': sms_pass,
                # 'start': yesterday.strftime('%d.%m.%Y'),
                # 'end': yesterday.strftime('%d.%m.%Y'),
                'start': '13.12.2024',
                'end': '13.12.2024',
                'cnt': 1000,
                'fmt': 3
            }
    response = requests.get('https://smsc.ru/sys/get.php', params=params)
    return response.json()

def create_record(message):
    n = 0
    with psycopg.connect(dbname='sms', user='postgres', password='postgres') as conn:
        for sms in message:
            with conn.cursor() as cur:
                cur.execute("""
                INSERT INTO sms(id_smsc, date_create, tel, mccmnc, operator, description, name_sender, quantity, status)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);
                """, (sms['id'], sms['send_date'], sms['phone'], sms['mccmnc'], sms['operator'], sms['message'],
                      sms['sender_id'], sms['sms_cnt'], sms['status_name']))
                conn.commit()
            print(n)
            n += 1
    conn.close()
    return

if __name__ == '__main__':
    config = configparser.ConfigParser()
    config.read('settings.ini')
    login = config['sms']['login']
    password = config['sms']['pass']
    # data = get_data(login, password)
    # create_record(data)
    # yesterday = date.today() - timedelta(days=1)
    # pprint(type(data[0]['send_date']))
    with psycopg.connect(dbname='sms', user='postgres', password='postgres') as conn:
        with conn.cursor() as cur:
            cur.execute("""
            INSERT INTO sms(id_smsc, date_create, tel, mccmnc, operator, description, name_sender, quantity, status)
            VALUES ('138121', '11.12.2024 15:01:30', '79042571859', '25020', 
            'Т2 Мобайл', 'Право по просроченному договору 01Ф24-0118727 от 26.09.2024 продано ОООЦУД - тел.: 8(4722)38-08-26, 
            сайт https://cudolg.ru/', 'bzaem.com', 2, 'Доставлено');
            SET datestyle = "ISO, DMY";
            """)
            conn.commit()
    conn.close()



