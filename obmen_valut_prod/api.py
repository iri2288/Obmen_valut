import fastapi
import pymysql
import datetime
import configparser



app = fastapi.FastAPI()


@app.get("/")
def root():
    return 'привет'

@app.get("/users")
def root():
    return ( 'kirill', 'ivan', 'paveul', 'anatoly' )

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
#def connect_to_db(host, port, user, password, db):
    #connection = pymysql.connect(host=host,port=port,user=user, password=password, db=db)
    #cursor = connection.cursor()
    #return connection, cursor

def connect_to_redis(redis_host, redis_port, redis_pass):
    redis_conn = redis.StrictRedis(host=redis_host, port=redis_port, password=redis_pass)
    return redis_conn


def connect_to_db():
    connection = pymysql.connect(host='127.0.0.1',port=3306,user='obmen', password='12345', db='BANK')
    cursor = connection.cursor()
    return connection, cursor


def get_valute_rate_from_db(connection, cursor,valute):
    local_valute = ('RUB','RUR')
    if valute in local_valute:
        return 1
    else:
        today = datetime.datetime.now().strftime('%Y.%m.%d')
        select_str = f'SELECT rate from valute_rate WHERE valute = "{valute}" AND date = "{today}";'
        cursor.execute(select_str)
        rate = float(cursor.fetchall()[0][0])
        return rate


@app.get("/valutes/{valute_name}")
def get_valute_rate(valute_name):
    connection, cursor = connect_to_db()
    rate = get_valute_rate_from_db(connection,cursor,valute_name)
    return {valute_name:rate}

@app.get("/convert")
def convert_valute(fv, sv, vcount):
    connection, cursor = connect_to_db()
    fv_rate = get_valute_rate_from_db(connection, cursor, fv)
    sv_rate = get_valute_rate_from_db(connection, cursor, sv)
    OUTVALUTE_COUNT = round((fv_rate * float(vcount)) / sv_rate, 2)
    return OUTVALUTE_COUNT