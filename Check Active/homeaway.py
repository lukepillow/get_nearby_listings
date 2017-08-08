import pandas as pd
import urllib
import json

import requests


# header from my laptop
headers = {'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36'}

# This sets the version for all future urllib objects to Mozilla/5.0 to avoid being denied.
class spoofURLopener(urllib.request.FancyURLopener):
	version = 'Mozilla/5.0'
urllib._urlopener = spoofURLopener()



def getUrlRequest(url):
	'''Returns a urllib request that bypasses the Airbnb 403: Forbidden (sometimes?)'''
	# Now it only avoids 403 for checkActive(). getAvailability() has been changed to use requests
	return urllib.request.Request(url, headers={'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36'})


def checkActiveUrl(url):
	'''Takes an airbnb url and returns True if still active.'''
	req = getUrlRequest(url)
	with urllib.request.urlopen(req) as homeawayPage:
		if homeawayPage.url == url:
			return True
		else:
			return False
