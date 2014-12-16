import subprocess
import json
import urllib2
import threading
import thread
import time
import pika

def getRequestUrl(key, location):
    return "http://api.wunderground.com/api/" + key + "/conditions/q/" + location + ".json"

frequency = 10
location = subprocess.check_output("cat zipcode.txt", shell=True)[:-1]
key = subprocess.check_output("cat Wundergroundkey.md", shell=True)[:-1]
request_url = getRequestUrl(key, location)

# The message broker host name or IP address
hostarg = "netapps.ece.vt.edu"
# The virtual host to connect to
vhostarg = "/2014/fall/archon" # Defaults to the root virtual host
# The routing key
routing_keyarg = "messagescroll"
#Login name
cred_login = "archon"
#Login password
cred_pass = "Power^Overwhelming96"

msg_broker = pika.BlockingConnection(
	pika.ConnectionParameters(host=hostarg, virtual_host=vhostarg, credentials=pika.PlainCredentials(cred_login, cred_pass, True)))

channel = msg_broker.channel()
channel.exchange_declare(exchange="razzledazzle_twist", type="direct")
channel.queue_declare(exclusive=True)

response = {"location": "", "weather": "", "temperature": ""}


while True:
    newZipCode = subprocess.check_output("cat zipcode.txt", shell=True)[:-1]
    if newZipCode != location:
	location = newZipCode
	request_url = getRequestUrl(key, location)
    weather_response = urllib2.urlopen(request_url)
    weather_result = json.loads(weather_response.read())["current_observation"]
    response["location"] = weather_result["display_location"]["full"]
    response["weather"] = weather_result["weather"]
    response["temperature"] = weather_result["temperature_string"]
    #channel.basic_publish(exchange="razzledazzle_twisted", routing_key=routing_keyarg, body=json.dumps(response, indent=4))
    channel.basic_publish(exchange="razzledazzle_twist", routing_key=routing_keyarg, body=response["temperature"])
    time.sleep(frequency)

if channel is not None:
	channel.close()
if msg_broker is not None:
	msg_broker.close()
