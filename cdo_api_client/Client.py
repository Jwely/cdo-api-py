from datetime import datetime, timedelta
import pandas as pd
from time import sleep
import requests
import warnings

from cdo_api_client.conf import API_HOST_URL, API_VERSION, DATETIME_FMT, ENDPOINTS
from cdo_api_client.util import segement_daterange
from cdo_api_client.exceptions import *


class BaseClient(object):
    def __init__(self, token, backup_token=None, verify_token=False):
        self.token = token
        self.backup_token = backup_token
        self.headers = {'token': token,
                        'Content-Type': 'application/json;charset=UTF-8'}
        self.host = API_HOST_URL
        self.version = API_VERSION
        self.verbose = True

        if verify_token:
            valid, response = self._test_auth()
            if not valid:
                raise AuthError(response.json()['message'])

    def _test_auth(self):
        r = self._get('datasets')
        if r.status_code == 400:
            return False, r
        return True, r

    @staticmethod
    def _validate_endpoint(endpoint):
        """ Compares endpoint against a list of valid endpoints """
        if endpoint in ENDPOINTS.keys():
            return True
        else:
            raise InvalidEndpoint("Endpoint '{}' is invalid! valid options are {}"
                                  .format(endpoint, ENDPOINTS))

    def _url(self, endpoint, *args, **kwargs):
        """
        Formats an api call url from args and host info, passing None's is OK.
        keyword arguments can be anything supported by the endpoint.
        """
        self._validate_endpoint(endpoint)
        baseurl = "/".join([self.host, 'api', self.version, endpoint, *args])
        if kwargs:
            joins = []
            for k, v in kwargs.items():
                if v is not None:
                    if isinstance(v, list):  # handles multiple value arguments
                        joins += ["{}={}".format(k, vv) for vv in v]
                    else:
                        joins.append("{}={}".format(k, v))
            url = "{}?{}".format(baseurl, "&".join(joins))
        else:
            url = baseurl
        if self.verbose:
            print(url)
        return url

    def _get(self, endpoint, *args, **kwargs):
        """ Passes args to url assembler and sends get request to that url"""
        self._validate_endpoint(endpoint)
        r = requests.get(url=self._url(endpoint, *args, **kwargs), headers=self.headers)
        if r.status_code == 429:
            message = r.json()['message']
            if "per second" in message:
                raise RequestsPerSecondLimitExceeded(message)
            elif "per day" in message:
                raise RequestsPerDayLimitExceeded(message)
        return r


class Client(BaseClient):
    def __init__(self, token, default_limit=1000, default_units='metric'):
        super(Client, self).__init__(token=token)
        self.default_limit = default_limit
        self.default_units = default_units

    def get(self, endpoint, *args, **kwargs):
        """
        Manages '_get' requests. Keeps API calls to 5 per second and segments
        requests when the responses are very long. Because multiple requests
        may be required, this is a generator object that yields the responses.
        """
        if "limit" not in kwargs.keys():
            kwargs['limit'] = self.default_limit
        if "units" not in kwargs.keys():
            kwargs['units'] = self.default_units

        try:
            response = self._get(endpoint, *args, **kwargs)
            yield response

            # if the response hits the limit, send more requests and yield responses
            if response.status_code == 200:
                resp_json = response.json()
                if 'metadata' in resp_json.keys():
                    meta = resp_json['metadata']['resultset']
                    offset = 0
                    limit = meta['limit']
                    count = meta['count']
                    while offset + limit < count:
                        offset += limit
                        kwargs['offset'] = offset
                        kwargs['limit'] = limit
                        yield self._get(endpoint, *args, **kwargs)

        except RequestsPerSecondLimitExceeded:
            sleep(1)
            yield from self.get(endpoint, **kwargs)
        except RequestsPerDayLimitExceeded:
            if self.backup_token is not None:
                print("Daily limit exceeded for primary token! Switching to backup token!")
                self.token = self.backup_token
                yield from self.get(endpoint, **kwargs)
            else:
                print("Try using a backup token next time!")
                raise

    @staticmethod
    def squash_results(responses):
        """ combines results from multiple responses into one list of results """
        results = []
        for r in responses:
            r_json = r.json()
            if 'results' in r_json.keys():
                results += r.json()['results']
        return results

    @staticmethod
    def results_to_dataframe(results):
        """ creates a pandas dataframe from a list of common results """
        if len(results) > 0:
            df = pd.DataFrame(results)
            if len(df) > 0:  # pivot tables cant be formed on empty dataframes
                df = df.pivot_table(values='value', index=['station', 'date'], columns='datatype')
            return df
        else:
            return pd.DataFrame()

    def list_endpoints(self):
        return ENDPOINTS

    def list_datasets(self):
        return self.squash_results(self.get('datasets'))

    def list_datacategories(self):
        return self.squash_results(self.get('datacategories'))

    def list_datatypes(self):
        return self.squash_results(self.get('datatypes'))

    def list_locationcategories(self):
        return self.squash_results(self.get('locationcategories'))

    def list_locations(self):
        return self.squash_results(self.get('locations'))

    def list_stations(self):
        return self.squash_results(self.get('stations'))

    def find_stations(self, datasetid, extent, startdate=None, enddate=None,
                      return_dataframe=True, **kwargs):
        """
        Returns list of stations within input bounding box.

        :param datasetid: one of the datasetids (see list_datasets())
        :param extent: dict with south, west, north and east keys. values in decimal degrees.
        :param startdate: startdate argument to search for station data availability
        :param enddate: enddate argument to search for station data availability
        :return:
        """
        get_args = dict(
            datasetid=datasetid,
            extent="{}, {}, {}, {}".format(
                extent['south'],
                extent['west'],
                extent['north'],
                extent['east']),
            **kwargs)

        if startdate is not None:
            if isinstance(startdate, datetime):
                startdate = startdate.strftime(DATETIME_FMT)
            if isinstance(startdate, str):
                get_args['startdate'] = startdate

        if enddate is not None:
            if isinstance(enddate, datetime):
                enddate = enddate.strftime(DATETIME_FMT)
            if isinstance(enddate, str):
                get_args['enddate'] = enddate

        results = self.squash_results(self.get('stations', **get_args))
        if return_dataframe:
            return pd.DataFrame(results)
        else:
            return results

    def get_station_data(self, datasetid=None, stationid=None, startdate=None, enddate=None,
                         return_dataframe=True, **kwargs):
        """
        Gets weather station data for given inputs.
        :param datasetid: required, see list_datasets() for options.
        :param stationid: required, station id. use find_stations() to help with this.
        :param startdate: datetime object for startdate of data query window
        :param enddate: datetime object for enddate of data query window
        :param return_dataframe: use True to return pandas dataframe of results
        :param kwargs: optional keyword arguments for get() call.
        :return: list of dicts with get results or pandas dataframe
        """

        for arg in ['datasetid', 'stationid', 'startdate', 'enddate']:
            if arg is None:
                raise RequiredArgumentError("{} is a required keyword argument!".format(arg))

        responses = []
        for start, end in segement_daterange(startdate, enddate, timedelta(days=365)):
            get_args = dict(
                datasetid=datasetid,
                stationid=stationid,
                startdate=start.strftime(DATETIME_FMT),
                enddate=end.strftime(DATETIME_FMT),
                **kwargs)

            responses += list(self.get('data', **get_args))

        results = self.squash_results(responses)
        if return_dataframe:
            return self.results_to_dataframe(results)
        else:
            return results

    def get_all_station_data(self, datasetid, extent, startdate=None, enddate=None,
                             return_dataframe=True, station_search_kwargs={},
                             data_filter_kwargs={}, **kwargs):
        """
        Returns all data from all available stations for given inputs

        :param datasetid: required, see list_datasets() for options.
        :param extent: dict with south, west, north and east keys. values in decimal degrees.
        :param startdate: datetime object for startdate of data query window
        :param enddate: datetime object for enddate of data query window
        :param return_dataframe: use True to return pandas dataframe of results
        :param station_search_kwargs: kwargs specifically for find_stations()
        :param data_filter_kwargs: kwargs specifically for get_station_data()
        :param kwargs: general kwargs to be passed to all function calls.
        :return: list of dicts with get results or pandas dataframe
        """
        stations = self.find_stations(
            datasetid=datasetid,
            extent=extent,
            startdate=startdate,
            enddate=enddate,
            return_dataframe=False,
            **station_search_kwargs,
            **kwargs)

        results = []
        for station in stations:
            try:
                results += self.get_station_data(
                    datasetid=datasetid,
                    stationid=station['id'],
                    startdate=startdate,
                    enddate=enddate,
                    return_dataframe=False,
                    **data_filter_kwargs,
                    **kwargs)
            except RequestsPerDayLimitExceeded:
                print("Operation aborted due to API request limits! Results are truncated!")
                pass

        if return_dataframe:
            results_df = pd.DataFrame(results)
            if len(results_df) > 0:
                results_df = results_df.pivot_table(
                    values='value', index=['station', 'date'], columns='datatype')
            return pd.DataFrame(stations), results_df
        else:
            return stations, results
