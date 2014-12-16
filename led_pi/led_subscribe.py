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

# Chat message callback
def on_chat_msg(channel, method, properties, msg_body):
	# Get the JSON data as a dictionary
	data = msg_body
	# Print out the data to look pretty
	print data
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


