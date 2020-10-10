import logger
import requests
import pandas as pd
import datetime

log = logger.get_logger("map_update")

# updating dataset of abmulance calls
def update_database(db_engine):
    features = requests.get('https://coronavirus.mash.ru/data.json').json()['features']

    date = pd.Series([datetime.datetime.now().date() for item in features], dtype='datetime64[ns]')
    address = pd.Series([item['properties']['hintContent'] for item in features], dtype='str')
    latitude = pd.Series([item['geometry']['coordinates'][0] for item in features], dtype='float')
    longitude = pd.Series([item['geometry']['coordinates'][1] for item in features], dtype='float')

    df = pd.DataFrame({'date': date, 'address': address, 'latitude': latitude, 'longitude': longitude})
    df.to_sql(name='covid_ambulances', con=db_engine, if_exists='replace')
