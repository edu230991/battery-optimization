import requests
import pandas as pd
import time
from matplotlib import pyplot as plt


def load_pv_data(years=[2016], latitude=45, longitude=22, tilt_angle=35,
         azimuth=180, tracking=False):
    """Loads PV data from Renewables Ninja given features
    
    Keyword Arguments:
        years {list} -- list of years to load data for. Note: API has a limit of 6/minute
                (default: {[2016]})
        latitude {int} -- (default: {45})
        longitude {int} -- (default: {22})
        tilt_angle {[type]} -- (default: {35azimuth=180})
        tracking {bool} -- If True, assumes tracking is available (default: {False})
    
    Returns:
        pd.DataFrame -- UTC-indexed dataframe with expected output from 1 kW plant
    """

    token = '965bd479ce6b7ef0d35861b042e50936adc3a13b'

    timeseries = 'pv'

    url = f'https://www.renewables.ninja/api/data/{timeseries}'

    df = pd.DataFrame()
    for year in years:
        print(f'Downloading year {year}')
        start_date = str(year) + '-01-01'
        end_date = str(year) + '-12-31'
        args = {
            'lat': latitude,
            'lon': longitude,
            'date_from': start_date,
            'date_to': end_date,
            'dataset': 'merra2',
            'capacity': 1.0,
            'system_loss': 10,
            'tracking': tracking * 1,
            'tilt': tilt_angle,
            'azim': azimuth,
            'format': 'json',
            'metadata': False,
            'raw': False
            }
        s = requests.session()
        s.headers = {'Authorization': 'Token ' + token}
        r = s.get(url, params=args)
        try:    
            this_year = pd.read_json(r.text, orient='index')
        except:
            if 'burst limit' in r.text:
                seconds = int(r.text.split(' ')[-2])
                print(f'API call limit reached, waiting {seconds} seconds...')
                time.sleep(seconds)
                r = s.get(url, params=args)
                this_year = pd.read_json(r.text, orient='index')

        df = df.append(this_year.tz_localize('UTC'))
        time.sleep(1)
    return df


def load_wind_data(years=[2016], latitude=45, longitude=22, height=100,
                   turbine='Vestas V80 2000'):
    """Loads wind power data from Renewables Ninja given features
    
    Keyword Arguments:
        years {list} -- list of years to load data for. Note: API has a limit of 6/minute
                (default: {[2016]})
        latitude {int} -- (default: {45})
        longitude {int} -- (default: {22})
        height {str} -- (default: {100})
        turbine {str} -- (default: {'Vestas+V80+2000'})       
    Returns:
        pd.DataFrame -- UTC-indexed dataframe with expected output from 1 kW plant
    """

    token = '965bd479ce6b7ef0d35861b042e50936adc3a13b'

    timeseries = 'wind'

    url = f'https://www.renewables.ninja/api/data/{timeseries}'

    df = pd.DataFrame()
    for year in years:
        print(f'Downloading year {year}')
        start_date = str(year) + '-01-01'
        end_date = str(year) + '-12-31'
        args = {
            'lat': latitude,
            'lon': longitude,
            'date_from': start_date,
            'date_to': end_date,
            'dataset': 'merra2',
            'capacity': 1.0,
            'height': height,
            'turbine': turbine,
            'format': 'json',
            'metadata': False,
            'raw': False
            }
        s = requests.session()
        s.headers = {'Authorization': 'Token ' + token}
        r = s.get(url, params=args)
        try:    
            this_year = pd.read_json(r.text, orient='index')
        except Exception as e:
            if 'burst limit' in r.text:
                seconds = int(r.text.split(' ')[-2])
                print(f'API call limit reached, waiting {seconds} seconds...')
                time.sleep(seconds)
                r = s.get(url, params=args)
                this_year = pd.read_json(r.text, orient='index')

        df = df.append(this_year.tz_localize('UTC'))
        time.sleep(1)
    return df


if __name__=='__main__':
    load_wind_data()