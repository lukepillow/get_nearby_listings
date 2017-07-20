from geolocate import *
import pandas as pd
import urllib.request
from bs4 import BeautifulSoup

url = 'http://www.abacuscapitalgroup.com/portfolio/'
portfolio = urllib.request.urlopen(url)
soup = BeautifulSoup(portfolio, 'html5lib')

results = []

for div in soup.find_all(class_='popup'):
	name = div.find('h2').text
	website = div.find(class_='link').text
	address = div.find(class_ = 'address').text
	geocode = getLocation(address)
	try:
		results.append((name, website, address, geocode[0], geocode[1]))
	except:
		print('Error!!')
		print(prettyAddress)
		print(geocode)

labels = ['Name','Website','Full Address', 'Lat', 'Lng']
results = pd.DataFrame.from_records(results, columns=labels)
results.to_csv('abacuscapitalgroup.csv')



