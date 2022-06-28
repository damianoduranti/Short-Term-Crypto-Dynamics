from sqlite3 import SQLITE_PRAGMA
from sys import api_version
from kafka import KafkaConsumer
import json
from typing import *
import psycopg2
import os

#local testing
""" consumer = KafkaConsumer('crypto',
                        group_id='spark',
                        api_version=(0, 11),
                        bootstrap_servers=['localhost:9092'],
                        auto_offset_reset='earliest',
                        value_deserializer=lambda m: json.loads(m.decode('utf-8')),
                        enable_auto_commit=True
                        ) """

#docker testing
consumer = KafkaConsumer(os.environ["KAFKA_TOPIC"],
                        group_id=os.environ["KAFKA_CONSUMER_GROUP"],
                        api_version=(0, 11),
                        bootstrap_servers=[os.environ["KAFKA_HOST"]],
                        auto_offset_reset='earliest',
                        value_deserializer=lambda m: json.loads(m.decode('utf-8')),
                        enable_auto_commit=True
                        )

#db connection parameters
hostname = "bigdatapostgres-federicozilli-bf3a.aivencloud.com"
database = "CRYPTODB"
username = "avnadmin"
pswrd = "AVNS_1owyZsR6_lLL93247eQ"
port_id = 18580

#connection and save the incoming entry
conn = psycopg2.connect(host = hostname, dbname=database, user= username, password=pswrd , port = port_id)
for message in consumer:
    try:
        cur = conn.cursor()
        print(message.value['date']+" "+message.value['time'])
        cur.execute(
            "INSERT INTO BTC VALUES (%s, %s, %s, %s, %s, %s, %s)",
            (message.value['date'],message.value['time'],message.value['open'],message.value['high'],message.value['low'],message.value['close'],message.value['volume'])
        )
        conn.commit()
    except: continue
    
conn.close()


"""     conn = psycopg2.connect(host = hostname, dbname=database, user= username, password=pswrd , port = port_id)
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO BTC VALUES (%s, %s, %s, %s, %s, %s, %s)",
        ("2022-06-24","17:28:00","20946","20952","20946","20946","20950")
    ) """
""" with open('/Users/damianoduranti/Desktop/kafka-spark-flink-container-main-2/data/test.csv', 'a', newline='') as file:
    writer = csv.writer(file)
    writer.writerow([date, time, message[6]['open'], message[6]['high'], message[6]['low'], message[6]['close'], message[6]['volume']])
now=str(datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
print(f"\rLast update: {now} ", end='', flush=True) """