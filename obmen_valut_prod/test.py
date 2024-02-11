import pymysql


connection = pymysql.connect(host='127.0.0.1', user='obmen', password='12345', database='BANK', port=3306)
cursor = connection.cursor()
#cursor.execute('ALTER TABLE BANK.valute_rate MODIFY COLUMN rate varchar(8) CHARACTER SET latin1 COLLATE latin1_swedish_ci DEFAULT NULL NULL;')
cursor.execute('ALTER TABLE BANK.valute_rate MODIFY COLUMN date varchar(10) CHARACTER SET latin1 COLLATE latin1_swedish_ci DEFAULT NULL NULL;')
data = cursor.fetchall()

print(data)
