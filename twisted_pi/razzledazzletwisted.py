#! /usr/bin/env python

from twisted.internet import reactor
from twisted.web.resource import Resource
from twisted.web.server import Site

import cgi
import subprocess
import pika

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
msg_broker = pika.BlockingConnection(pika.ConnectionParameters(host=hostname, virtual_host=vhost, credentials=pika.PlainCredentials(user, password, True)))
# Setup the exchange
channel = msg_broker.channel()
channel.exchange_declare(exchange="razzledazzle_twist", type="direct")
channel.queue_declare(exclusive=True)

class RazzleDazzlePage(Resource):
	isLeaf = True
	def render_GET(self, request):
		return subprocess.check_output("cat razzledazzlepage.html", shell=True)

	def render_POST(self, request):
		# Set POST message to a variable
		output=cgi.escape(request.args["message-field"][0])
		zipCodeText = cgi.escape(request.args["zipCode-field"][0])
		if len(zipCodeText) > 0 and int(zipCodeText) >= 0 and int(zipCodeText) < 100000:
			subprocess.check_output("echo " + zipCodeText + "> ../weather_pi/zipcode.txt", shell=True)
		else:
			# Send the message
			channel.basic_publish(exchange="razzledazzle_twist", routing_key=rout_key, body=output)
		#return """
		#	<html>
		#		<body>You submitted: %s</body>
		#	</html>
		#""" % (cgi.escape(request.args["message-field"][0]), )
		return subprocess.check_output("cat razzledazzlepage.html", shell=True)
		

factory = Site(RazzleDazzlePage())
reactor.listenTCP(10000, factory)
reactor.run()

# Close the connection
if channel is not None:
    channel.close()
if msg_broker is not None:
    msg_broker.close()
