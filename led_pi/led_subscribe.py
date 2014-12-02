#! /usr/bin/env python

__author__ = ["Zak Grove", "Connor Brizendine"]

import subprocess
import signal
import sys
import time
import json
import getopt
import pika

channel = None
msg_broker = None

cpu_xtremez = [0, 0]
interface_xtremez = {}

# The following two methods are taken from Tad. They allow the program to gracefully exit.
# When a signal like Ctrl-C is entered by the user, these methods catch it and exit.
def on_quit(signal, stack_frame):
	print "\nCaught Signal: " + str(signal)
	print "Cleaning up..."
	# Add code to close any connections here
	if channel is not None:
		channel.close()
	if msg_broker is not None:
		msg_broker.close()
	print "Quitting"
	sys.exit()

# Sets up quit handlers to run when "signal_number" is received
def set_custom_quit_handler(signal_number):
	try:
		previous_handler = signal.signal(signal_number, on_quit)
	except ValueError, ve:
		print "Signal not supported: " + str(signal_number)  + ": " + str(ve)

# Chat message callback
def on_chat_msg(channel, method, properties, msg_body):
	# Get the JSON data as a dictionary
	data = json.loads(msg_body)
	# If the interface_xtremez list is empty, then we have no initial data to go off on.
	# So, go ahead and fill it and the cpu_xtremez list up.
	if len(interface_xtremez) == 0:
		cpu_xtremez[0] = data["cpu"]
		cpu_xtremez[1] = data["cpu"]
		for interface in data["net"]:
			interface_xtremez[interface] = {"rx": [data["net"][interface]["rx"], data["net"][interface]["rx"]], "tx": [data["net"][interface]["tx"], data["net"][interface]["tx"]]}
	else:
		# Compare the extremes to see if we have a new extreme
		if cpu_xtremez[0] > data["cpu"]:
			cpu_xtremez[0] = data["cpu"]
		if cpu_xtremez[1] < data["cpu"]:
			cpu_xtremez[1] = data["cpu"]
		for interface in interface_xtremez:
			for stat in interface_xtremez[interface]:
				if interface_xtremez[interface][stat][0] > data["net"][interface][stat]:
					interface_xtremez[interface][stat][0] = data["net"][interface][stat]
				if interface_xtremez[interface][stat][1] < data["net"][interface][stat]:
					interface_xtremez[interface][stat][1] = data["net"][interface][stat]

		# Print out the data to look pretty
		print "cpu: " + str(data["cpu"]) + " [Hi: " + str(cpu_xtremez[1]) + ", Lo: " + str(cpu_xtremez[0]) + "]"
		for interface in interface_xtremez:
			print interface + ": rx=" + str(data["net"][interface]["rx"]) + " B/s [Hi: " + str(interface_xtremez[interface]["rx"][1]) +\
				" B/s, Lo: " + str(interface_xtremez[interface]["rx"][0]) + " B/s], tx=" +\
				str(data["net"][interface]["tx"]) + " B/s [Hi: " + str(interface_xtremez[interface]["tx"][1]) +\
				" B/s, Lo: " + str(interface_xtremez[interface]["tx"][0]) + " B/s]"
		print

# The message broker host name or IP address
hostarg = None
# The virtual host to connect to
vhostarg = "/" # Defaults to the root virtual host
# The credentials to use
credentialsarg = None
# The routing key
routing_keyarg = None

# Set on_quit() to be called when SIGTERM is received
set_custom_quit_handler(signal.SIGTERM)
# Set on_quit() to be called when SIGINT is received (i.e. when ^C is pressed)
set_custom_quit_handler(signal.SIGINT)

# Parsing command line parameters
try:
	opts, args = getopt.getopt(sys.argv[1:], "b:p:c:k:")
except getopt.GetoptError:
	print "ERROR: Please format a proper command:\npistatsview.py -b msg_broker_ip [-p virtual_host] [-c login:password] -k routing_key"
	sys.exit(2)
for opt, arg in opts:
	if opt == "-b":
		hostarg = arg
	elif opt == "-p":
		vhostarg = arg
	elif opt == "-c":
		credentialsarg = arg
		if ':' not in credentialsarg:
			print "ERROR: Please format the -c like the following:\n -c login:password"
			sys.exit()
	elif opt == "-k":
		routing_keyarg = arg
# Ensure that the user specified the required arguments
	if hostarg is None:
		print "You must specify a message broker to connect to using the -b parameter:\npistatsview.py -b msg_broker_ip [-p virtual_host] [-c login:password] -k routing_key"
		sys.exit()

if routing_keyarg is None:
	print "You must specify a routing key to subscribe to"
	sys.exit()


cred_list = credentialsarg.split(':')
cred_login = cred_list[0]
cred_pass = cred_list[1]


# Connect to the message broker
msg_broker = pika.BlockingConnection(
	pika.ConnectionParameters(host=hostarg, virtual_host=vhostarg, credentials=pika.PlainCredentials(cred_login, cred_pass, True)))

print "Connected to message broker"

# Setup the exchange
channel = msg_broker.channel()
channel.exchange_declare(exchange="pi_utilization", type="direct")

# Create an exclusive queue for receiving messages
ch = msg_broker.channel()
my_queue = ch.queue_declare(exclusive=True)

# Bind the queue to the chat room exchange
ch.queue_bind(exchange="pi_utilization", queue=my_queue.method.queue, routing_key=routing_keyarg)

# Setup the callback for when a subscribed message is received
ch.basic_consume(on_chat_msg, queue=my_queue.method.queue, no_ack=True)
print "Entering pi info..."

# Start a blocking consume operation
ch.start_consuming()


