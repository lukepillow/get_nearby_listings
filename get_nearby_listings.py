"""
This program will take a csv file as input and generate nearby short-term rental listings

## Input format:  csv file, range in miles
## CSV file format 1:   Apartment.com url
## CSV file format 2:   Apartment_name, latitude, longitude
## Output file 1 summary:    Apart, bnb < 3m, bnb < 1m, bnb < 0.1m, hmawy < 3m, hmawy < 1m, 
                            hmawy < 0.1m,   (counts)
## Output file 2 detail within 0.1 mile:  Apart, bnb URL < 0.1m,  hmawy URL < 0.1m, Match_or_not
## Print out how many apartments url found in the database 
"""

import psycopg2
import pandas as pd
import csv 
import datetime as dt
import time
import sys
from geopy.distance import vincenty

today = dt.datetime.today().strftime("%Y_%m_%d")
PATH = "~/work/"


def get_range(lat,lon,miles = 1):
    lat_range = 0.012*miles
    lon_range = 0.012*miles
    q = ('lat < {} & lat > {} & lng < {} & lng > {}'.format(
            lat+lat_range,lat-lat_range,lon+lon_range,lon-lon_range))
    return q


def get_listings_detail(apart,str_data):
    result = []
    for index,row in apart.iterrows():
        q = get_range(row['lat'],row['lon'],0.2)
        within_1_mile = str_data.query(q)
        #writer.writerow(row['url'],)
        l = len(within_1_mile)
        if l > 0:
            for i,str_row in within_1_mile.iterrows():
                apart_location = (row['lat'],row['lon'])
                str_location = (str_row['lat'],str_row['lng'])
                actual_distance = vincenty(apart_location,str_location).miles
                result.append([row['url'],str(str_row['url']),actual_distance])
    return result


def count_nearby(row, str_data,distance):
    q = get_range(row['lat'],row['lon'],distance)
    within_range = str_data.query(q)
    return len(within_range)

def get_nearby_rentals(apart,bnb,hmawy):
    for distance in [3,1,0.2]:
        apart['bnb_within_{}_miles'.format(distance)] = apart.apply(count_nearby, axis = 1, args = (bnb,distance))
    for distance in [3,1,0.2]:
        apart['hmawy_within_{}_miles'.format(distance)] = apart.apply(count_nearby, axis = 1, args = (hmawy,distance))
    return apart


print 'Number of arguments:', len(sys.argv), 'arguments.'
input_file = sys.argv[1]
file_name = input_file.split('/')[-1].replace('.csv','')

if ".csv" not in input_file:
    print("Please use csv file")
try:
    input_df = pd.read_csv(input_file)
except:
    print("error in load data")

print input_df.head()


if 'url' not in list(input_df):
    print("Need to have at least one column named 'url'")

elif 'lat' not in list(input_df):
    urls = list(input_df['url'])
    apart_all = pd.read_csv(PATH + 'apart_all.csv')
    apart_match = apart_all[apart_all['url'].isin(urls)]
    print("For total {} URLs in {}, we found {} matches ".format(len(urls),sys.argv[1],len(apart_match)))
    input_df = apart_match[['url','lat','lon']]
    missing_urls = input_df[~input_df['url'].isin(list(apart_match['url']))]
    print missing_urls

if 'lat' in list(input_df) and 'lon' in list(input_df):
    print("Load bnb data")
    bnb_US = pd.read_csv(PATH + 'bnb_US_selected_features1.csv')

    print("Load hmawy data")
    hmawy_US = pd.read_csv(PATH + 'data/all_hmawy_2017-03-09_1.csv')


    print("counting nearyby STRs")
    apart_counts = get_nearby_rentals(input_df,bnb_US,hmawy_US)
    apart_counts.to_csv(PATH + 'data_output/{}_nearby_STR.csv'.format(file_name),index = False)

    print("Get nearest Homeaway listings")

    hmawy_detail = pd.DataFrame(get_listings_detail(input_df,hmawy_US),columns = ['Apart','hmawy','hmaway_distance'] )
    print("finished hmawy")
    hmawy_detail.to_csv(PATH + 'data_output/{}_hmawy_detail.csv'.format(file_name),index = False)

    print("Get nearest Airbnb listings")
    bnb_detail = pd.DataFrame(get_listings_detail(input_df,bnb_US),columns = ['Apart','bnb','bnb_distance'])
    bnb_detail.to_csv(PATH + 'data_output/{}_bnb_detail.csv'.format(file_name),index = False)

    print("finished all")









