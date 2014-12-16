#! /usr/bin/env python

import subprocess
import signal
import sys
import time
import json
import getopt
import pika

channel = None
msg_broker = None
xmas=['sudo','./led-matrix','-r','16','-D','1','-t','15','Merry_Christmas.ppm']
newyear=['sudo','./led-matrix','-r','16','-D','1','-t','15','Happy_New_Year.ppm']
joynloves=['sudo','./led-matrix','-r','16','-D','1','-t','15','Joy_and_Love_to_the_World.ppm']
hohoho=['sudo','./led-matrix','-r','16','-D','1','-t','15','Ho_Ho_Ho.ppm']
holiday=['sudo','./led-matrix','-r','16','-D','1','-t','15','Happy_Holidays.ppm']

def print_message(input_message):
    if input_message == "Merry Christmas!":
        subprocess.Popen(xmas)
        time.sleep(16)
    elif input_message == "Happy New Year!":
        subprocess.Popen(newyear)
        time.sleep(16)
    elif input_message == "Joy and love to the world!":
        subprocess.Popen(joynloves)
        time.sleep(16)
    elif input_message == "Ho Ho Ho!!":
        subprocess.Popen(hohoho)
        time.sleep(16)
    elif input_message == "Happy Holidays!":
        subprocess.Popen(holiday)
        time.sleep(16)
	

# Chat message callback
def on_chat_msg(channel, method, properties, msg_body):
    # Get the JSON data as a dictionary
    data = msg_body
    # Print out the data to look pretty
    print data
    print_message(data)
    print






#The IP address
hostname = "netapps.ece.vt.edu"
#Virtual host to connec to 
vhost = "/2014/fall/archon"
#User name and password
user = "archon"
password = "Power^Overwhelming96"
#Topic to suscribe to
rout_key = "messagescroll"

# Connect to the message broker
msg_broker = pika.BlockingConnection(
	pika.ConnectionParameters(host=hostname, virtual_host=vhost, credentials=pika.PlainCredentials(user, password, True)))

# Setup the exchange
channel = msg_broker.channel()
channel.exchange_declare(exchange="razzledazzle_twist", type="direct")

# Create an exclusive queue for receiving messages
ch = msg_broker.channel()
my_queue = ch.queue_declare(exclusive=True)

# Bind the queue to the chat room exchange
ch.queue_bind(exchange="razzledazzle_twist", queue=my_queue.method.queue, routing_key=rout_key)

# Setup the callback for when a subscribed message is received
ch.basic_consume(on_chat_msg, queue=my_queue.method.queue, no_ack=True)

# Start a blocking consume operation
ch.start_consuming()


