import flask
import pika
from flask import request, jsonify
from flask_cors import CORS
import logging
import json
import sqlite3
import configparser
import hashlib

logging.basicConfig(filename='app.log',level=logging.DEBUG
                    ,format='%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s')

#Config_File
config = configparser.RawConfigParser()
config.read('user.ini')
limit = configparser.RawConfigParser()
limit.read('data.ini')

app = flask.Flask(__name__)
CORS(app)


@app.route('/', methods=['GET'])
def home():
    return "Smartsense"

@app.route('/api/get/default', methods=['GET'])
def get_default():
    connection = pika.BlockingConnection(
        pika.ConnectionParameters('localhost',5672,'/data',pika.PlainCredentials('guest','guest')))
    channel = connection.channel()
    channel.queue_declare(queue='data_queue', durable=True)

    temp = "{\"default}"
    channel.basic_publish(exchange='',
                          routing_key='data_queue',
                          body = temp,
                          properties=pika.BasicProperties(delivery_mode=2,))

    connection.close()
    return "<h1>Successfully added!</h1>"

@app.route('/api/get/temperature', methods=['GET'])
def get_temperature():
    temperature = {}
    conn = sqlite3.connect('temperature_data.sqlite')
    c = conn.cursor()
    cursor = conn.execute("SELECT temperature FROM data")
    for i in cursor:
        temperature['temperature'] = i
      
    response = jsonify(temperature)
    #response.headers.add('Access-Control-Allow-Origin', '*')
    #response.headers.add('Access-Control-Allow-Headers', '*')
    #response.headers.add('Access-Control-Allow-Methods', '*')    
    return response

@app.route('/api/login', methods=['POST'])
def login():
    req_data = request.get_json()
    req_pass = req_data['password']
    req_pass = hashlib.sha256(req_pass.encode()).hexdigest()
    #print(req_pass)
    #print(config['AUTHORIZATION']['password'])
    reply = {}
    if(req_data['username'] == config['AUTHORIZATION']['username'] and req_pass == config['AUTHORIZATION']['password']):
        reply['message'] = "no" #return 'no' to match the configuration of the web page
                                #but it is successfully login
    else:
        reply['message'] = "yes"    #Indicate fail to login

    response = jsonify(reply)
    #response.headers.add('Access-Control-Allow-Origin', '*')
    #response.headers.add('Access-Control-Allow-Headers', '*')
    #response.headers.add('Access-Control-Allow-Methods', '*')
    return response

@app.route('/api/get/data', methods=['GET'])
def get_data():
    data = {}
    name = []
    temp = []
    i = 0
    for j in limit['THRESHOLD_DATA']:
        i+=1
        name.append(j)
    data['count'] = i
    for info in name:
        temp.append(limit['THRESHOLD_DATA'][str(info)])
    data['name'] = name
    data['threshold'] = temp
    response = jsonify(data)
    return response

if __name__ == '__main__':
    app.run(debug=True, port=5000)
