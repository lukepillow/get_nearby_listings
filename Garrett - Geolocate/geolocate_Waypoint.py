from geolocate import *
import pandas as pd
import time

def getLocation(address):
	'''Function from geolocate rewritten to additionally return address.'''
	google_response = getPossibleLocations(address)
	if len(google_response) == 0:
		print('No locations found for that address:')
	elif len(google_response) > 1:
		print('More than one possible location found for that address')
		for possibleLocation in google_response:
			print(getAddressFromJSON(possibleLocation))
		result = getGeocodeFromJSON(google_response[0])
		return (result['lat'], result['lng'])
	else: #Only one result found
		result = getGeocodeFromJSON(google_response[0])
		return (getAddressFromJSON(google_response[0]),result['lat'], result['lng'])


import urllib.request
from bs4 import BeautifulSoup

url = 'http://www.waypointresidential.com/'

portfolio = urllib.request.urlopen(url+'property.aspx')
soup = BeautifulSoup(portfolio, 'html5lib')
pagesToCrawl = soup.find(id='m-east').find_all('a') #list of pages to crawl

def makeAddress(name, place):
	return name + ', ' + place

results = []
for page in pagesToCrawl:
	time.sleep(1)
	portfolio = urllib.request.urlopen(url+page['href'])
	soup = BeautifulSoup(portfolio, 'html5lib')
	for location in soup.find_all(class_='pinsd pin-down'):
		time.sleep(1)
		name = str.strip(location.find('h2').text)
		place = str.strip(location.find('h3').text)
		prettyAddress = makeAddress(name, place)
		geocode = getLocation(prettyAddress)
		try:
			results.append((name, place, geocode[0], geocode[1], geocode[2]))
		except:
			print('Error!!')
			print(prettyAddress)
			print(geocode)
			results.append((name, place, 'error','error','error'))

labels = ['Name', 'Place', 'Address', 'Lat', 'Lng']
results1 = pd.DataFrame.from_records(results, columns=labels)
results1.to_csv('waypointresidential.csv')



