import requests
import psycopg
from pprint import pprint

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

data = get_data()
pprint(data[0])

with psycopg.connect(dbname='sms', user='postgres', password='postgres') as conn:
    with conn.cursor() as cur:
        cur.execute("""
        INSERT INTO sms(id_smsc, date_create, tel, mccmnc, operator, description, name_sender, quantity, ip, status)
        VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
        """, data[0]['id'], data[0]['last_date'], data[0]['phone'], data[0]['mccmnc'], data[0]['operator'], data[0]['message'], data[0]['sender_id'])
        conn.commit()
conn.close()


