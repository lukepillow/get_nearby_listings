import psycopg2
import pandas as pd
import csv
import airbnb
import ast

from geopy.distance import vincenty
from geopy.distance import great_circle


def login_to_database():
	'''Wrapper for connect_postgresql() that uses credentials stored in "credentials.py"'''
	try:
		import credentials
		conn, cur = connect_postgresql(host=credentials.host, user=credentials.user, password=credentials.password)
		return conn, cur
	except:
		print("Error reading credentials.py and connecting to server. Do you have credentials.py in the same directory?")

def temp():
	'''Temporary solution to load the buildings and registered users data from csv files instead of database.'''
	buildingsDataFrame = pd.read_csv('buildings.csv')
	registeredDataFrame = pd.read_csv('registered.csv')
	return buildingsDataFrame, registeredDataFrame


def connect_postgresql(
                       host='',
                       user='',
                       password=''):
    """Set up the connection to postgresql database"""
    try:
        conn = psycopg2.connect(
                "dbname ='postgres' host={} user={} \
                 password={}".format(host,user,password))
        cur = conn.cursor()
        return conn,cur
    except Exception as e:
        print("Unable to connect to the database Error is ", e)
		
def get_range(lat,lon,miles = 1):
	'''Luke Code. Generates the sql query for lat and lon range.'''
	lat_range = 0.012*miles
	lon_range = 0.012*miles
	q = ('lat < {} AND lat > {} AND lng < {} AND lng > {}'.format(lat+lat_range,lat-lat_range,lon+lon_range,lon-lon_range))
	return q		

def getBuildings(conn):
	'''Gets all of the buildings data from the database and returns it in a pandas DataFrame.'''
	registered_buildings_query = '''SELECT c.id,c.name,pa.address_line_1, address_line_2, city, state, postal_code,latitude,longitude 
	FROM "postal_addresses" pa
	JOIN communities c
	ON pa.postally_addressable_id=c.id
	WHERE postally_addressable_type='Building'
	ORDER BY id;'''
	
	# Load the buildings into a Pandas DataFrame
	buildingsDataFrame = pd.read_sql_query(registered_buildings_query, conn)
	# Get rid of null entries
	buildingsDataFrame = buildingsDataFrame[not buildingsDataFrame['name'] == None]
	
	return buildingsDataFrame

def getListings(lat, lon, miles, conn):
	'''Gets all the listings within a certain distance of the provided lat, lon point.'''
	tablename = 'crawled_bnb_listing_detail_2017_05_02'
	listings_query = '''SELECT * FROM ''' + tablename + ''' WHERE ''' + get_range(lat, lon, miles)
	listingsDataFrame = pd.read_sql_query(listings_query, conn)
	return listingsDataFrame


def processBuilding(building, conn):
	'''Processes a single building and returns the results as a list of lists.'''
	lat, lon = building['latitude'], building['longitude']
	
	# Gets a DataFrame containing all listings within .3 miles-ish
	listings = getListings(lat,lon, .3, conn)
	
	results = []
	
	for listing in listings.iterrows():
		listing = listing[1]
		id = listing['id']
		try:
			nameData = ast.literal_eval(listing['user1'])
			if not nameData == -1:
				name = nameData['user']['first_name']
			else:
				name = ''
		except:
			print("Error getting name.")
			print(listing['user1'])
			name = ''
		distance = vincenty((lat,lon),(listing['lat'], listing['lng'])).miles
		active = airbnb.checkActive(id)
		if active:
			availabililty = getAvailability(str(id))
		else:
			availabililty = None
		results.append([building['name'], building['address_line_1'], id,'',name,distance,availabililty,'https://www.airbnb.com/rooms/'+str(id), active])
	
	#labels = ['Building', 'Address', 'ID', 'Match?', 'Name', 'Distance', 'TotalAvailability', 'URL', 'Active?']
	#resultsDF = pd.DataFrame.from_records(results, columns = labels)
	
	#with open(building['name'] + '.csv', 'w', errors='replace') as output:
	#	resultsDF.to_csv(output, encoding='utf-8')
	
	return results


def getUsers(conn):
	registered_users_query = '''SELECT resident_units.id,listings.service_property_id,buildings.community_id,buildings.name,postal_addresses.latitude,postal_addresses.longitude FROM resident_units
	INNER JOIN listings ON listings.resident_unit_id = resident_units.id
	INNER JOIN units ON resident_units.unit_id = units.id
	INNER JOIN buildings ON units.building_id = buildings.id
	LEFT JOIN postal_addresses on buildings.community_id = postal_addresses.postally_addressable_id
	WHERE listings.service_property_id  is not null and
	postal_addresses. postally_addressable_type='Building' order by service_property_id;'''
	
	# Load the users into a Pandas DataFrame
	usersDataFrame = pd.read_sql_query(registered_users_query, conn)
	# Get rid of null entries
	#usersDataFrame = usersDataFrame[not usersDataFrame['latitude'] == None]
	
	return usersDataFrame

def getAvailability(id):
	'''Returns the number of availabilities for the next 3 months.'''
	availabililty = airbnb.getAvailability(id)
	count = 0
	for date in sorted(availabililty, key = lambda x: x[1]):
		if date[2] == True:
			count += 1
	return int(count)


def process(buildingsDF, registeredDF, conn):
	'''Function to process all the buildings and output the data to "Output.csv"'''
	results = []
	for building in buildingsDF.iterrows():
		building = building[1] # Sets the variable to the actual builing data, building[0] is an index int
		results += processBuilding(building, conn)
	
	registered_ids = set(registeredDF['service_property_id']) # Sets run much faster for id lookup
	for i in range(len(results)): # For loop for checking if the id is in the system
		if int(results[i][2]) in registered_ids:
			results[i][3] = True # Marks "Match?" as True, because it must be from the right building if in the system.
			results[i].append(True)
		else:
			results[i].append(False)
	
	labels = ['Building','Address','ID', 'Match?', 'Name', 'Distance', 'TotalAvailability', 'URL', 'Active?', 'In System?']
	resultsDF = pd.DataFrame.from_records(results, columns = labels)
	with open('Output.csv', 'w', errors='replace') as f:
		resultsDF.to_csv(f, encoding='utf-8')

def go():
	conn, cur = connect_postgresql()
	buildingsDF, registeredDF = temp()
	process(buildingsDF, registeredDF, conn)