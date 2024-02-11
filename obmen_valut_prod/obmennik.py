import pymysql
import configparser
import datetime
import redis

def get_data_from_config():
    config = configparser.ConfigParser()
    config.read('obmennik.conf')
    db_host = config.get('database', 'host')
    db_port = int(config.get('database', 'port'))
    db_user = config.get('database', 'user')
    db_password = config.get('database', 'pass')
    db = config.get('database', 'database')
    redis_host = config.get('redis','host')
    redis_port = int(config.get('redis', 'port'))
    redis_pass = config.get('redis', 'pass')
    return db_host, db_port, db_user, db_password, db, redis_host, redis_port, redis_pass

def connect_to_db(host, port, user, password, db):
    connection = pymysql.connect(host=host,port=port,user=user, password=password, db=db)
    cursor = connection.cursor()
    return connection, cursor

def get_valute_rate(connection, cursor,valute):
    local_valute = ('RUB','RUR')
    if valute in local_valute:
        return 1
    else:
        today = datetime.datetime.now().strftime('%Y.%m.%d')
        select_str = f'SELECT rate from valute_rate WHERE valute = "{valute}" AND date = "{today}";'
        cursor.execute(select_str)
        rate = float(cursor.fetchall()[0][0])
        return rate

def connect_to_redis(redis_host, redis_port, redis_pass):
    redis_conn = redis.StrictRedis(host=redis_host, port=redis_port, password=redis_pass)
    return redis_conn

def get_rate_from_redis(redis_conn, valute):
    rate = redis_conn.get(valute)
    if rate:
        rate = float(rate.decode())
    return rate

def set_rate_to_redis(redis_conn, valute, valute_rate):
    redis_conn.set(valute, valute_rate, ex= 600)
    return True




if __name__ == '__main__':
    connection = None
    INVALUTE = input('Введите валюту, которую Вы хотите поменять: ')
    OUTVALUTE = input('Введите валюту, на которую вы хотите поменять: ')
    INVALUTE_COUNT = float(input('Сколько Вы хотите поменять? : '))
    start_time = datetime.datetime.now()

    db_host, db_port, db_user, db_password, db, redis_host, redis_port, redis_pass = get_data_from_config()
    red_conn = connect_to_redis(redis_host, redis_port, redis_pass)
    INVALUTE_RATE = get_rate_from_redis(red_conn, INVALUTE)
    OUTVALUTE_RATE = get_rate_from_redis(red_conn, OUTVALUTE)
    print(INVALUTE_RATE, OUTVALUTE_RATE, 'Получено из redis')
    if not INVALUTE_RATE:
        connection, cursor = connect_to_db(db_host, db_port, db_user, db_password, db)
        INVALUTE_RATE = get_valute_rate(connection, cursor, INVALUTE)
        set_rate_to_redis(red_conn, INVALUTE, INVALUTE_RATE)
        print(INVALUTE, INVALUTE_RATE, 'ПОЛУЧЕНО ИЗ БД')
    if not OUTVALUTE_RATE:
        if not connection:
            connection, cursor = connect_to_db(db_host, db_port, db_user, db_password, db)
            OUTVALUTE_RATE = get_valute_rate(connection, cursor, OUTVALUTE)
            set_rate_to_redis(red_conn, OUTVALUTE, OUTVALUTE_RATE)
            print(OUTVALUTE, OUTVALUTE_RATE, 'ПОЛУЧЕНО ИЗ БД')

    OUTVALUTE_COUNT = round((INVALUTE_COUNT * INVALUTE_RATE)/OUTVALUTE_RATE, 2)
    print(f'Клиенту нужно выдать {OUTVALUTE_COUNT} {OUTVALUTE}')
    print(INVALUTE_RATE, OUTVALUTE_RATE)
    end_time = datetime.datetime.now()
    work_time = end_time - start_time
    print(f'Время работы {work_time}')

#except pymysql.err.OperationalError as MySQLOE:
     #print(f'евозможно установить соединение с базой данных \n{MySQLOE}')
# except IndexError as IE:
     #print(f'вы ввели некорректное наименование валюты \n{IE}')
