from cdo_api_py import Client
import pandas as pd
from datetime import datetime
from pprint import pprint

# initialize a client with a developer token ,
# note 5 calls per second and 1000 calls per day limit for each token
token = "my token here!"
my_client = Client(token, default_units=None, default_limit=1000)
# the other valid option for units is 'standard', and default_limit maxes out at 1000

# first lets see what endpoints are associated with the API
# you can read more about this from NOAAs NCDC at
# https://www.ncdc.noaa.gov/cdo-web/webservices/v2#gettingStarted
pprint(my_client.list_endpoints())

# request a list of available datasets (about 11) with
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

# lets define the date range we're interested in as well,  December 2016
startdate = datetime(2016, 12, 1)
enddate = datetime(2016, 12, 31)

# after examining the available datasets, we decided 'GHCND' is the one we want,
# and that we really want daily min and max temperatures
datasetid='GHCND'
datatypeid=['TMIN', 'TMAX', 'PRCP']

# lets find stations that meet all our criteria
stations = my_client.find_stations(
    datasetid=datasetid,
    extent=extent,
    startdate=startdate,
    enddate=enddate,
    datatypeid=datatypeid,
    return_dataframe=True)
pprint(stations)

# we can get big lists of station data with
big_df = pd.DataFrame()
for rowid, station in stations.iterrows():  # remember this is a pandas dataframe!
    station_data = my_client.get_data_by_station(
        datasetid=datasetid,
        stationid=station['id'],    # remember this is a pandas dataframe
        startdate=startdate,
        enddate=enddate,
        return_dataframe=True,  # this defaults to True
        include_station_meta=True   # flatten station metadata with ghcnd readings
    )
    pprint(station_data)
    big_df = pd.concat([big_df, station_data], sort=False)

# Now we can do whatever we want with our big dataframe. Lets sort it by date and save it
print(big_df)
big_df = big_df.sort_values(by='date').reset_index()
big_df.to_csv('dc_ghcnd_example_output.csv')
