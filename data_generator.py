import pika
import json
from datetime import datetime
import sys, random, requests, time, os, logging

logging.basicConfig(filename='data_gen.log',level=logging.DEBUG
                    ,format='%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s')


connection = pika.BlockingConnection(
        pika.ConnectionParameters('localhost',5672,'/data',pika.PlainCredentials('user1','password')))
channel = connection.channel()
channel.queue_declare(queue='data_queue', durable=True)
channel.exchange_declare(exchange='logs',
                         exchange_type='fanout')


random.seed(500)

while(True):
    temperature = random.randint(10,60)

    temp = "{\"Temperature\" : "+str(int(temperature))+"}"

    channel.basic_publish(exchange='logs',
                          routing_key='data_queue',
                          body = temp,
                          properties=pika.BasicProperties(delivery_mode=2,))
            
    
    print("[x] Sent: %s"%temp)

    time.sleep(5)
