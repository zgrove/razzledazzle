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
password = Power^Overwhelming96
#Topic to suscribe to
routing_key = "messagescroll"
# Connect to the message broker
msg_broker = pika.BlockingConnection(pika.ConnectionParameters(host=hostname, virtual_host=vhost, credentials=pika.PlainCredentials(user, password, True)))
# Setup the exchange
channel = msg_broker.channel()
channel.exchange_declare(exchange="razzledazzle_twist", type="direct")
channel.queue_declare(exclusive=True)

class RazzleDazzlePage(Resource):
	isLeaf = True
	def render_GET(self, request):
		return subprocess.check_output("cat razzledazzlepage.html", shell=True);

	def render_POST(self, request):
		# Set POST message to a variable
		output=cgi.escape(request.args["message-field"][0])
		return
		"""
			<html>
				<body>You submitted: %s</body>
			</html>
		""" % (cgi.escape(request.args["message-field"][0]), )
		

factory = Site(RazzleDazzlePage())
reactor.listenTCP(10000, factory)
reactor.run()
