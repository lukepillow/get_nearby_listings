import pandas as pd
import time
import airbnb
import homeaway

def load_csv(filename, columnName):
	csv_dataframe = pd.read_csv(filename)
	return csv_dataframe[columnName].tolist()


def checkListings(urlList, sleepTime = 0):
	results = []
	for url in urlList:
		time.sleep(sleepTime)	# Sleep for a bit to throw off detection
		if isAirbnb(url):
			results.append((url, airbnb.checkActiveUrl(url)))
		elif isHomeaway(url):
			results.append((url, homeaway.checkActiveUrl(url)))
		else:
			print("Error, URL not recognized:")
			print(url)
	
	labels = ['URL', 'Active?']
	resultsDF = pd.DataFrame.from_records(results, columns = labels)
	return resultsDF

def writeOutput(resultsDF):
	with open('Output.csv', 'w', errors='replace') as f:
		resultsDF.to_csv(f, encoding='utf-8')

def isAirbnb(url):
	return 'airbnb.com' in url

def isHomeaway(url):
	return 'homeaway.com' in url