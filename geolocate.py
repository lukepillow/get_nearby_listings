import json
import requests

def getRequest(address):
	'''Returns the google api request for an address string.'''
	base = 'https://maps.googleapis.com/maps/api/geocode/json?address='
	return base + address
	
def getPossibleLocations(address):
	'''Returns a list of possible locations parsed in json for a given address.'''
	api_response = requests.get(getRequest(address))
	api_response = json.loads(api_response.text)
	
	if not api_response['status'] == 'OK':
		
		if api_response['status'] == 'ZERO_RESULTS':
			print('No Results found for that address')
		
		elif api_response['status'] == 'OVER_QUERY_LIMIT':
			print("You have exceeded google geocode api limit for the day")
			print("As of July 19, 2017, the limit was 2,500 free requests per day with a max of 50 per second.")
			print("Additional requests may be purchased by google for $0.50 / 1000 through their api key program.")
		
		elif api_response['status'] == 'REQUEST_DENIED':
			print('Request has been denied by the Google server.')
		
		elif api_response['status'] == 'INVALID_REQUEST':
			print('The API request was invalid.')
		
		else:
			print('Status returned something other than OK:')
			print(api_response['status'])
	
	for location in api_response['results']:
		if not 'street_address' in getTypeFromJSON(location) and not 'premise' in getTypeFromJSON(location) and not 'establishment' in getTypeFromJSON(location):
			print('Possible location is NOT a street address:')
			print(getAddressFromJSON(location))
			print('It has the following types:')
			print(str(getTypeFromJSON(location)))
	
	else:
		return api_response['results']

def getGeocodeFromJSON(json):
	'''Takes a location's json representation and returns its latitude and longitude in a dictionary.'''
	return json['geometry']['location']

def getAddressFromJSON(json):
	'''Takes a location's json representation and returns its formatted address.'''
	return json['formatted_address']

def getTypeFromJSON(json):
	'''Takes a location's json representation and returns a list of its types.
	Useful for checking if some results make sense.'''
	return json['types']

def getLocation(address):
	'''Takes an address string and returns the lat and lng in a tuple.
	Prints irregularities found.'''
	google_response = getPossibleLocations(address)
	if len(google_response) == 0:
		print('No locations found for that address: ', address)
	elif len(google_response) > 1:
		print('More than one possible location found for that address')
		for possibleLocation in google_response:
			print(getAddressFromJSON(possibleLocation))
		result = getGeocodeFromJSON(google_response[0])
		return (result['lat'], result['lng'])
	else: #Only one result found
		result = getGeocodeFromJSON(google_response[0])
		return (result['lat'], result['lng'])

# Due to biasing, '580 Market Street' and '580 Market St' return different results
# This can be rectified by biassing towards a boundary or a region
# However, when more exact, such as '580 Market Street, San Fran', then it doesn't matter'
# Google api gives 2500 free requests per day at 50 per second

