import pandas as pd
import urllib
import json

import requests

# api_key from my laptop, logged into gconway@hmc.edu
api_key = 'd306zoyjsyarp7ifhu67rjxn52tv0t20'

# header from my laptop
headers = {'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36'}

# This sets the version for all future urllib objects to Mozilla/5.0 to avoid being denied.
class spoofURLopener(urllib.request.FancyURLopener):
	version = 'Mozilla/5.0'
urllib._urlopener = spoofURLopener()


#This code could be rewritten better using requests instead of urllib
def getUrl(id, month=8):
	'''Returns the url for the api request.'''
	currency = 'USD'
	locale = 'en'
	month = str(month)
	year = '2017'
	count = '3'
	format = 'with_conditions'
	return 'https://www.airbnb.com/api/v2/calendar_months?key='+api_key+'&currency='+currency+'&locale='+locale+'&listing_id='+str(id)+'&month='+month+'&year='+year+'&count='+count+'&_format='+format

def getUrlRequest(url):
	'''Returns a urllib request that bypasses the Airbnb 403: Forbidden (sometimes?)'''
	# Now it only avoids 403 for checkActive(). getAvailability() has been changed to use requests
	return urllib.request.Request(url, headers={'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36'})

def checkActive(id):
	'''Takes an airbnb id and returns True if still active.'''
	url = 'https://www.airbnb.com/rooms/' + str(id)
	req = getUrlRequest(url)
	with urllib.request.urlopen(req) as airbnbPage:
		if airbnbPage.url == url:
			return True
		else:
			return False

def checkActiveUrl(url):
	'''Takes an airbnb url and returns True if still active.'''
	req = getUrlRequest(url)
	with urllib.request.urlopen(req) as airbnbPage:
		if airbnbPage.url == url:
			return True
		elif airbnbPage.url == url[:-2]: # Hard check addition for .0 urls...
			return True
		else:
			return False

			
# NOT YET DONE
def checkActiveUrl2(url):
	'''Takes an airbnb url and returns True if still active.'''
	req = requests.get(url, headers=headers)
	#if(req.statusCode
	if airbnbPage.url == url:
		return True
	else:
		return False

def getAvailability(id):
	'''Returns a set containing the parsed json data for the dates of the next 3 months.'''
	# This uses a set to avoid overlap from the airbnb api between months
	availability = set()
	calendarJSON = json.loads(requests.get(getUrl(id), headers=headers).text)
	for month in calendarJSON['calendar_months']:
		for day in month['days']:
			availability.add((id,day['date'],day['available'],day['price']['local_currency'],day['price']['local_price'],day['price']['native_currency'],day['price']['native_price']))
	return availability

