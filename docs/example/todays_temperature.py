from cdo_api_py import Client
import pandas as pd
from datetime import datetime, timedelta
from pprint import pprint

token = "neUpeFDrjywfWJbLfcwyrPFcFitqUFEG"
my_client = Client(token, default_units='metric')

extent = {
    "north": 39.1,
    "south": 39.0,
    "east": -76.6,
    "west": -77.0,
}

end_date = datetime(2017, 1, 8)
start_date = end_date - timedelta(days=7)

stations = ['GHCND:US1DCDC0001', 'GHCND:US1DCDC0002', 'GHCND:US1DCDC0003']
result = my_client.get_data_by_station(datasetid='GHCND', stationid=stations[0],
                                       # startdate=start_date, enddate=end_date,
                                       #datatypeid=['TMAX', 'TMIN'],
                                       #includemetadata=True
                                       )
result.to_csv("temp.csv")
print(result)


# get all data for a a one day period.
# result = my_client.squash_results(my_client.get('data', datasetid='GHCND', startdate=start_date, enddate=end_date))
# print(result)

# result = my_client.find_stations(datasetid='GHCND', extent=extent, return_dataframe=True)



# result = my_client.results_to_dataframe(
#         my_client.squash_results(
#         my_client.get('data', datasetid='GHCND', startdate=start_date, enddate=end_date, extent=extent)))
# result.to_csv('temp.csv')
