import json
import urllib2
#import pika

url = urllib2.urlopen('http://api.wunderground.com/api/7caf7ee2e937f875/conditions/q/IA/24060.json')

def get_conditions():
	string = url.read()
	parsed_string = json.loads(string)
	conditions = str(parsed_string["current_observation"]["icon"])
	temperature = str(parsed_string["current_observation"]["temp_f"])
	return conditions,temperature


#Main
#Set up message broker. Using class RabbitMQ for testing. Will use actual server once it is ready
#msg_broker=pika.BlockingConnection(pika.ConnectionParameters(host="netapps.ece.vt.edu",virtual_host="sandbox",credentials=pika.PlainCredentials("ECE4564-Fall2014","13ac0N!",True)))
weather,temperature = get_conditions()
print weather
print temperature
