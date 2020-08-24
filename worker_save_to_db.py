import pika
from flask import request, jsonify
import logging
import json
import time
import re
import sqlite3
#import pydblite
#from pydblite import Base

sleepTime = 5
print(' [*] Sleeping for ', sleepTime, ' seconds.')
time.sleep(sleepTime)

print(' [*] Connecting to server ...')
#connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq'))
#channel = connection.channel()
#channel.queue_declare(queue='task_queue', durable=True)


connection = pika.BlockingConnection(pika.ConnectionParameters('localhost',5672,'/data',pika.PlainCredentials('user1','password')))
#connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq',5672,'/',pika.PlainCredentials('guest','guest')))
channel = connection.channel()
channel.exchange_declare(exchange='logs', exchange_type='fanout')
result = channel.queue_declare(queue='data_queue', durable=True)
queue_name = result.method.queue

channel.queue_bind(exchange='logs', queue=queue_name)

print(' [*] Waiting for messages.')

conn = sqlite3.connect('temperature_data.sqlite')
c = conn.cursor()

sql_create_table = """ CREATE TABLE IF NOT EXISTS data (
                                        id integer PRIMARY KEY, 
                                        temperature integer NOT NULL
                                    ); """


def callback(ch, method, properties, body):
    print(" [x] %r" % body)
    temp = str(body)
    temp = temp[2:-1]
    a = re.split(r'\s',temp)
    b = a[2][:-1]
    #print(b)
    
    conn = sqlite3.connect('temperature_data.sqlite')
    c = conn.cursor()
    #conn.execute(sql_create_table)
    conn.execute("INSERT or REPLACE INTO data (id,temperature) VALUES (?,?)",(1,int(b)));
    conn.commit()
    conn.close()  

channel.basic_consume(
    queue=queue_name, on_message_callback=callback, auto_ack=True)
channel.start_consuming()
    
