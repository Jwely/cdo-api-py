[![PyPI version](https://badge.fury.io/py/cdo-api-py.svg)](https://badge.fury.io/py/cdo-api-py)

# cdo-api-py
Python interface to cdo api, which is described in full detail [here](https://www.ncdc.noaa.gov/cdo-web/webservices/v2#gettingStarted)
Built to allow quick and easy query for weather data to pandas dataframe objects.

## Installation

```
pip install cdo-api-py
```
or for python3
```
pip3 install cdo-api-py
```

## Example Use

To start, you'll need a token, which you can request [here](https://www.ncdc.noaa.gov/cdo-web/token).

Import a few libraries and instantiate a client. default_units and default_limit are optional keyword arguments.
```python
from cdo_api_py import Client
import pandas as pd
from datetime import datetime
from pprint import pprint
token = "my_token_here"     # be sure not to share your token publicly
my_client = Client(token, default_units='metric', default_limit=1000)
```

Once a client has been initialized, we can define a few variables to outline what we really want.
Since this repo is just a python client to interface with the CDO api, the user has the option
to use keyword arguments that are passed directly to the API and aren't detailed here, so you
may need to browse the options available for the dataset of choice.

The example we will use is the very common GHCN-Daily (ghcnd) weather set. We have found
the north, south, east, and west lat/lon coordinates that describe the bounding box of the
general Washington DC area. Next we define the dates we're interested in (optional) and
the dataset id. As an added step, we really want specific values from the dataset so lets
save those in a list as well as datatypeid (optional).

```python
extent = {
    "north": 39.14,
    "south": 38.68,
    "east": -76.65,
    "west": -77.35,
}

startdate = datetime(2016, 12, 1)
enddate = datetime(2016, 12, 31)

datasetid='GHCND'
datatypeid=['TMIN', 'TMAX', 'PRCP']
```

Now we pass all these into a single function call to our client `my_client` to find stations of interest.
We can use `return_dataframe=True` to automatically assemble the information into a dataframe.
```python
stations = my_client.find_stations(
    datasetid=datasetid,
    extent=extent,
    startdate=startdate,
    enddate=enddate,
    datatypeid=datatypeid,
    return_dataframe=True)
pprint(stations)
```

Now that we have a list of stations that have data useful to us, we can iterate through
the list of stations and pass the stationid argument to a `get_data_by_station` method.
```python
for rowid, station in stations.iterrows():  # remember this is a pandas dataframe!
    station_data = my_client.get_data_by_station(
        datasetid=datasetid,
        stationid=station['id'],
        startdate=startdate,
        enddate=enddate,
        return_dataframe=True,
        include_station_meta=True   # flatten station metadata with ghcnd readings
    )
    pprint(station_data)
```

We can modify this slightly to concatenate all the small dataframes into one big dataframe
and save it as a CSV.
```python
big_df = pd.DataFrame()
for rowid, station in stations.iterrows():  # remember this is a pandas dataframe!
    station_data = my_client.get_data_by_station(
        datasetid=datasetid,
        stationid=station['id'],
        startdate=startdate,
        enddate=enddate,
        return_dataframe=True,
        include_station_meta=True   # flatten station metadata with ghcnd readings
    )
    pprint(station_data)
    big_df = pd.concat([big_df, station_data])

print(big_df)
big_df = big_df.sort_values(by='date').reset_index()
big_df.to_csv('dc_ghcnd_example_output.csv')
```

see all the example code here: [DC weather data example](docs/example/dc_weather_data.py)

It may take a bit of manual searching to familiarize yourself with the NOAA CDO offerings, but
once you figure out the arguments you'd like to use, this client should make it quite easy
to automate weather data retrievals. There are many requirements and limits as to the nature of
requests that the server will allow, and this client will automatically determine if a request
must be split up into multiple smaller pieces and create them, send them, and piece the
results back together into a single coherent response without any additional effort.

***

You can explore the endpoints available, either at the CDO documentation site or quickly with
```python
pprint(my_client.list_endpoints())

# returned at time of writing
{'data': 'A datum is an observed value along with any ancillary attributes at '
         'a specific place and time.',
 'datacategories': 'A data category is a general type of data used to group '
                   'similar data types.',
 'datasets': 'A dataset is the primary grouping for data at NCDC',
 'datatypes': 'A data type is a specific type of data that is often unique to '
              'a dataset.',
 'locationcategories': 'A location category is a grouping of similar '
                       'locations.',
 'locations': 'A location is a geopolitical entity.',
 'stations': 'A station is a any weather observing platform where data is '
             'recorded.'}
```

At the time of writing, there are about 11 available datasets, they are `['GHCND', 'GSOM', 'GSOY', 'NEXRAD2', 'NEXRAD3', 'NORMAL_ANN', 'NORMAL_DLY', 'NORMAL_HLY', 'NORMAL_MLY', 'PRECIP_15', 'PRECIP_HLY']`. View the full details with:
```python
pprint(my_client.list_datasets())
```

There are more than 1000 datatypes, but you can see them all with
```python
pprint(my_client.list_datatypes())
```


## TODO:
* Another example or two for non GHCND
* Build a gh-pages branch with sphinx
