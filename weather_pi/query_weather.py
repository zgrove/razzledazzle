import subprocess
import json
import urllib2
import threading
import thread
import time

def getRequestUrl(key, location):
    return "http://api.wunderground.com/api/" + key + "/conditions/q/" + location + ".json"

frequency = 10
location = "24060"
key = subprocess.check_output("cat Wundergroundkey.md", shell=True)[:-1]
request_url = getRequestUrl(key, location)

def queryWeather():
	global location
	print "Query thread started"
	while(location != "stop"):
		lock.acquire()
		response = urllib2.urlopen(request_url)
		weather_result = json.loads(response.read())["current_observation"]
		print
		print "Location: " + weather_result["display_location"]["full"]
		print "Weather: " + weather_result["weather"]
		print "Temp: " + weather_result["temperature_string"]
		print "Humidity: " + weather_result["relative_humidity"]
		print "Wind Speed: " + str(weather_result["wind_mph"])
		print
		print "Enter a new ZIP code if ya wanna: "
		lock.release()
		time.sleep(frequency)
	print "Query thread ended"

def getUserInput():
	global location
	global request_url
	print "Input thread started"
	while(location != "stop"):
		user_input = raw_input()
		print "Enter a new ZIP code if ya wanna: "
		lock.acquire()
		location = user_input
		request_url = getRequestUrl(key, location)
		lock.release()
	print "Input thread ended"

lock = threading.Lock()

try:
   thread.start_new_thread(queryWeather, ())
   thread.start_new_thread(getUserInput, ())
except:
   print "Error: unable to start threads"

while(True):
	pass
