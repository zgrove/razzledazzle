#! /usr/bin/env python

__author__ = ["Zak Grove", "Connor Brizendine"]

import subprocess
import signal
import sys
import time
import json
import getopt
import pika

message_broker = None
channel = None

# This method grabs and parses output from /proc/uptime
def get_CPU_usage():
	info = subprocess.check_output("cat /proc/uptime", shell=True).split(" ")
	return (float(info[0]), float(info[1]))

# This method grabs, parses, and formats output from /proc/net/dev
def get_throughput():
	info = subprocess.check_output("num1=`wc -l < /proc/net/dev`;num2=$((num1-2));tail -n $num2 /proc/net/dev", shell=True).split("\n")
	result = {}
	for interface in info:
		if len(interface) <= 0:
			continue
		interface_data = filter(lambda a: a != '', interface.split(" "))
		result[interface_data[0][:-1]] = {"rx": int(interface_data[1]), "tx": int(interface_data[9])}
	return result

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
	print "ERROR: Please format a proper command:\npistatsd.py -b msg_broker_ip [-p virtual_host] [-c login:password] -k routing_key"
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
		print "You must specify a message broker to connect to using the -b parameter:\npistatsd.py -b msg_broker_ip [-p virtual_host] [-c login:password] -k routing_key"
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
# Setup the exchange
channel = msg_broker.channel()
channel.exchange_declare(exchange="pi_utilization", type="direct")
channel.queue_declare(exclusive=True)

# Gets time-1 stats for cpu and throughput
old_uptime, old_idletime = get_CPU_usage()
old_throughput = get_throughput()
old_time = time.time()
time.sleep(1)

response = {"net": {}, "cpu": 0}
# Continue to get throughput and cpu every 1 second
while True:
	current_uptime, current_idletime = get_CPU_usage()
	current_throughput = get_throughput()
	current_time = time.time()
	response["cpu"] = 1.0 - (current_idletime - old_idletime)/(current_uptime - old_uptime)
	temp_throughput = {}
	for t in current_throughput:
		temp_throughput[t] = {"rx":(current_throughput[t]["rx"] - old_throughput[t]["rx"]) / (current_time - old_time),"tx":(current_throughput[t]["tx"] - old_throughput[t]["tx"]) / (current_time - old_time)}
	response["net"] = temp_throughput
	final_msg = json.dumps(response, indent=4)
        #print final_msg

	# Send the message
	channel.basic_publish(exchange="pi_utilization",
						  routing_key=routing_keyarg,
						  body=final_msg)

	old_uptime = current_uptime
	old_idletime = current_idletime
	time.sleep(1)

# Close the connection
if channel is not None:
	channel.close()
if msg_broker is not None:
	msg_broker.close()
