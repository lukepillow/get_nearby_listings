import json
import requests
import sys
import pandas as pd
import time

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
			print('Possible location is NOT a street address, premise, or establishment:')
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
	
	error = None
	result = (None, None)
	
	google_response = getPossibleLocations(address)
	
	if len(google_response) == 0:
		print('No locations found for that address: ', address)
		error = 'No locations found.'
	
	
	elif len(google_response) > 1:
		print('More than one possible location found for that address:')
		for possibleLocation in google_response:
			print(getAddressFromJSON(possibleLocation))
		error = 'Multiple possible locations.'
		
		rawResult = getGeocodeFromJSON(google_response[0])
		result = (rawResult['lat'], rawResult['lng'])

	else: #Only one result found
		rawResult = getGeocodeFromJSON(google_response[0])
		result = (rawResult['lat'], rawResult['lng'])
	
	return (address, result[0], result[1], error)

		
if __name__ == '__main__':
	# Get the file to open from the arguments
	input_file = sys.argv[1]
	if '.csv' not in input_file:
		print('Please use a csv file.')
	try:
		input_df = pd.read_csv(input_file)
	except:
		print('Error in opening file.')
	
	
	# Open the file and locate the address column
	address = None
	if 'address' not in list(input_df) and 'Address' not in list(input_df) and 'adr' not in list(input_df):
		print('Please have at least one column labeled address')
	
	elif 'address' in list(input_df):
		address = 'address'
	elif 'Address' in list(input_df):
		address = 'Address'
	else:
		address = 'adr'
		
		
	# Output results
	results = []
	for address in input_df[address]:
		time.sleep(.5)
		results.append(getLocation(address))
	
	labels = ['Address', 'Latitude', 'Longitude', 'Error?']
	results = pd.DataFrame.from_records(results, columns=labels)
	results.to_csv(input_file[:-4] + '_OUTPUT.csv')

# Due to biasing, '580 Market Street' and '580 Market St' return different results
# This can be rectified by biassing towards a boundary or a region
# However, when more exact, such as '580 Market Street, San Fran', then it doesn't matter'
# Google api gives 2500 free requests per day at 50 per second
# Is this github mergable?
