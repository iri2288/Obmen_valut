import configparser
import requests
import pymysql
import datetime
import sys
import os
import logging

def notification():
    pass


def get_data_from_cb(url):
    logging.debug('Start func get_data_from_cb')
    result = requests.get(url)
    logging.debug('data successfully received from the Central Bank')
    raw_json = result.json()['Valute']
    logging.debug('json successfully received')
    real_rates = {}
    logging.debug('An empty dictionary has been created')
    for valute in raw_json:
        raw_rate = float(raw_json[valute]['Value'])
        nominal = int(raw_json[valute]['Nominal'])
        real_rate = round(raw_rate/nominal, 3)
        real_rates[valute] = real_rate
    logging.debug(f'function return data {real_rates}')

    return real_rates;

def insert_data_to_db(connection, cursor,valute_dict):
    today = datetime.datetime.now().strftime('%Y.%m.%d')
    print(today)
    for valute in valute_dict.keys():
        rate =valute_dict[valute]
        insert_str =  f'INSERT into valute_rate values("{today}","{valute}","{rate}")'
        print(insert_str)
        cursor.execute(insert_str)
    connection.commit()
    return True


def get_data_from_config():
    config = configparser.ConfigParser()
    config.read('get_data_from_cb.conf')
    cburl = config.get('general', 'cburl')
    host = config.get('database', 'host')
    port = int(config.get('database', 'port'))
    user = config.get('database', 'user')
    password = config.get('database', 'pass')
    db = config.get('database', 'database')
    return cburl, host, port, user, password, db

def write_log(h):

    pass


def connect_to_db(host, port, user, password, db):
    connection = pymysql.connect(host=host,port=port,user=user, password=password, db=db)
    cursor = connection.cursor()
    return connection, cursor

if __name__=='__main__':
    logging.basicConfig(filename='get_data_from_cb.log', level=logging.DEBUG, format='[%(asctime)s] [%(levelname)s] => %(message)s')
    logging.info('try to get date')
    today = datetime.datetime.now().strftime('%Y.%m.%d')
    logging.info(f'date successfully received {today}')
    filename = f'{today}.ok'
    logging.info('begin test flag file')
    if os.path.exists(filename):
        logging.info('comlete test flag file ')
        sys.exit()
    logging.info('continue test - flag not exist ')
    insert_result = False
    logging.info('begin get info from config')
    cburl, host, port, user, password, db = get_data_from_config()
    logging.info('info from config received')
    try:
        logging.info('try to get info from Central Bank')
        valute_dict = get_data_from_cb(cburl)
        logging.info('info from Central Bank received')
        logging.info('try to make connection to database')
        print(valute_dict)
        connection, cursor = connect_to_db(host, port, user, password, db)
        logging.info('connection to database successfully complete')
        logging.info('try to insert info to database')
        insert_result = insert_data_to_db(connection, cursor, valute_dict)
        logging.info('info inserted to database')
        logging.info('test info in database')
        if insert_result:
            open(filename,'a').close()
            logging.info('info insert to database successfully, flag file was created!')
    except requests.exceptions.ConnectionError as CE:
        #print(f'не удалось подключться к сайту ЦБ \n{CE}')
        logging.info(f'не удалось подключться к сайту ЦБ \n{CE}')
    except requests.exceptions.JSONDecodeError as JDE:
        #print(f'не удалось разобрать json \n{JDE}')
        logging.info(f'не удалось разобрать json \n{JDE}')
