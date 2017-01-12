[![PyPI version](https://badge.fury.io/py/cdo-api-py.svg)](https://badge.fury.io/py/cdo-api-py)

# cdo-api-py
Python interface to cdo api. Built to allow quick and easy query for weather
data to pandas dataframe objects.

## Installation
Notes:



```
pip install cdo-api-py
```
or for python3
```
pip3 install cdo-api-py
```

* Read more [here](https://www.ncdc.noaa.gov/cdo-web/webservices/v2#gettingStarted)


## Example Use
``` python
from cdo_api_client import Client

import pandas as pd
from datetime import datetime
from pprint import pprint


# initialize a client with a developer token ,
# note 5 calls per second and 1000 calls per day limit for each token
token = "my_token_here"
my_client = Client(token, default_units='metric')
# the other valid option for units is 'standard'

# first lets see what endpoints are associated with the API
# you can read more about this from NOAAs NCDC at
# https://www.ncdc.noaa.gov/cdo-web/webservices/v2#gettingStarted
pprint(my_client.list_endpoints())

# reaquest a list of available datasets (about 11) with
pprint(my_client.list_datasets())

# there are more than 1000 datatypes, but you can see them all with
pprint(my_client.list_datatypes())


# define the extent we are interested in. in this case the DC metro area.
extent = {
    "north": 39.14,
    "south": 38.68,
    "east": -76.65,
    "west": -77.35,
}

# lets define the date range we're interested in as well December 2016
startdate = datetime(2016, 12, 1)
enddate = datetime(2016, 12, 31)

# after examining the available datasets, we decided 'GHCND' is the one we want,
# and that we really want daily min and max temperatures
datasetid='GHCND'
datatypeid=['TMIN', 'TMAX']

# lets find stations that meet all our criteria, of given dataset ID, within our
# defined geographic area, with dataon TMIN and TMAX in December 2016.
stations = my_client.find_stations(
    datasetid=datasetid,
    extent=extent,
    startdate=startdate,
    enddate=enddate,
    datatypeid=['TMIN', 'TMAX'])
pprint(stations)

# we can get big lists of station data with
for station in stations:
    station_data = my_client.get_station_data(
        datasetid=datasetid,
        stationid=station['id'],
        startdate=startdate,
        enddate=enddate,
        return_dataframe=False,  # this defaults to True
        limit=1000)
    pprint(station_data)

# this format is quite verbose, but we can easly get these as pandas dataframes with
# a 'return_dataframe=True' keyword argument, and concatenate them together.
big_df = pd.DataFrame()
for station in stations:
    station_df = my_client.get_station_data(
        datasetid='GHCND',
        stationid=station['id'],
        startdate=startdate,
        enddate=enddate,
        return_dataframe=True,
        limit=1000)
    big_df = pd.concat([big_df, station_df])

# and now we have one dataframe with all the stuff we want in it!
print(big_df)

# Finally, the laziest case combines all of these together into one main function
# which gives us a dataframe of all stations used, as well as a dataframe
# with all available data from those stations.
stations, data = my_client.get_all_station_data(
    datasetid=datasetid,
    extent=extent,
    startdate=startdate,
    enddate=enddate,
    return_dataframe=True,
    datatypeid=['TMIN', 'TMAX'])
print(stations)
print(data)
```
