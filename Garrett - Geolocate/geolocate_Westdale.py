from geolocate import *
import pandas as pd
import urllib.request
from bs4 import BeautifulSoup

url = 'http://www.westdalecommunities.com/searchlisting.aspx?ftst=&LocationGeoId=0&zoom=10&cmbBeds=-1&cmbBaths=-1&cmb_PetPolicy=Indifferent&renewpg=1&PgNo='

results = []
for i in range(1,8):
	portfolio = urllib.request.urlopen(url+str(i))
	soup = BeautifulSoup(portfolio, 'html5lib')
	for div in soup.find_all(class_='parameters hidden mapPoint'):
		name = div.find(class_='propertyName').text
		address = div.find(class_='propertyAddress').text
		lat = div.find(class_='propertyLat').text
		lng = div.find(class_='propertyLng').text
		results.append((name, address, lat, lng))


labels = ['Name', 'Full Address', 'Lat', 'Lng']
results = pd.DataFrame.from_records(results, columns=labels)
results.to_csv('westdalecommunities.csv')



