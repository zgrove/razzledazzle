#! /usr/bin/env python

from twisted.internet import reactor
from twisted.web.resource import Resource
from twisted.web.server import Site

import cgi
import subprocess

class RazzleDazzlePage(Resource):
	isLeaf = True
	def render_GET(self, request):
		return subprocess.check_output("cat razzledazzlepage.html", shell=True);

	def render_POST(self, request):
		return """
			<html>
				<body>You submitted: %s</body>
			</html>
		""" % (cgi.escape(request.args["message-field"][0]), )

factory = Site(RazzleDazzlePage())
reactor.listenTCP(10000, factory)
reactor.run()
