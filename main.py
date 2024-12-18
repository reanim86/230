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

# data = get_data()
# pprint(data[0])
def create_record(message):
    for sms in message:
        with psycopg.connect(dbname='sms', user='postgres', password='postgres') as conn:
            with conn.cursor() as cur:
                cur.execute("""
                INSERT INTO sms(id_smsc, date_create, tel, mccmnc, operator, description, name_sender, quantity, status)
                VALUES
                    (%s, %s, %s, %s, %s, %s, %s, %s, %s);
                """, (sms['id'], sms['send_date'], sms['phone'], sms['mccmnc'], sms['operator'], sms['message'],
                      sms['sender_id'], sms['sms_cnt'], sms['status_name']))
                conn.commit()
        conn.close()
    return

if __name__ == '__main__':
    config = configparser.ConfigParser()
    config.read('settings.ini')
    login = config['sms']['login']
    password = config['sms']['pass']
    data = get_data(login, password)
    create_record(data)
    # yesterday = date.today() - timedelta(days=1)
    # pprint(data[0])



