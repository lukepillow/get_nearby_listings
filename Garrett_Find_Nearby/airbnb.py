import pandas as pd
import urllib
import json

import requests

api_key = 'd306zoyjsyarp7ifhu67rjxn52tv0t20'
headers = {'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36'}

class spoofURLopener(urllib.request.FancyURLopener):
	version = 'Mozilla/5.0'
urllib._urlopener = spoofURLopener()


def getUrl(id, month=8):
	currency = 'USD'
	locale = 'en'
	month = str(month)
	year = '2017'
	count = '3'
	format = 'with_conditions'
	return 'https://www.airbnb.com/api/v2/calendar_months?key='+api_key+'&currency='+currency+'&locale='+locale+'&listing_id='+str(id)+'&month='+month+'&year='+year+'&count='+count+'&_format='+format

def getUrlRequest(url):
	# Returns a request that bypasses the Airbnb 403: Forbidden
	return urllib.request.Request(url, headers={'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36'})

def checkActive(id):
	url = 'https://www.airbnb.com/rooms/' + str(id)
	req = getUrlRequest(url)
	with urllib.request.urlopen(req) as airbnbPage:
		if airbnbPage.url == url:
			return True
		else:
			return False

def getAvailability(id):
	availability = set()
	calendarJSON = json.loads(requests.get(getUrl(id), headers=headers).text)
	for month in calendarJSON['calendar_months']:
		for day in month['days']:
			availability.add((id,day['date'],day['available'],day['price']['local_currency'],day['price']['local_price'],day['price']['native_currency'],day['price']['native_price']))
	return availability

