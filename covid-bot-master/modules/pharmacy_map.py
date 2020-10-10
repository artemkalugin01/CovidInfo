import geopy.distance
import geopy
import pandas as pd
import requests
import ssl
from bs4 import BeautifulSoup
from geopy import Nominatim
import logger
import map_extension

ssl._create_default_https_context = ssl._create_unverified_context
log = logger.get_logger("pharmacy_map")


# get content method
def get_content(lon=None, lat=None):
    log.info(f"Pharmacy map creator started [{lon}][{lat}]")

    locator = Nominatim(user_agent='bot')
    radius = 1000

    # read full dataset
    raw = requests.get("http://overpass-api.de/api/interpreter?data=<query type='node'><around lat='" +
                       str(lat) +
                       "' lon='" +
                       str(lon) +
                       "' radius='" +
                       str(radius) +
                       "'/></query><print/>").text

    data = BeautifulSoup(raw, features='xml')
    pharmacies = data.find_all('tag', {'k': 'amenity', 'v': 'pharmacy'})

    address = pd.Series([locator.reverse((pharmacy.parent['lat'], pharmacy.parent['lon']), timeout=10000).address
                         for pharmacy in pharmacies], dtype=str)
    latitude = pd.Series([pharmacy.parent['lat'] for pharmacy in pharmacies], dtype=float)
    longitude = pd.Series([pharmacy.parent['lon'] for pharmacy in pharmacies], dtype=float)

    data = pd.DataFrame({'address': address, 'latitude': latitude, 'longitude': longitude})
    data['distance'] = data.apply(lambda row:
                                  geopy.distance.distance((row['latitude'], row['longitude']), (lat, lon)).km, axis=1)
    # getting area borders
    min_lat = data['latitude'].min()
    max_lat = data['latitude'].max()
    min_lon = data['longitude'].min()
    max_lon = data['longitude'].max()

    data = data.sort_values(by=['distance'])
    message = f"Ближайшие аптеки в радиусе {radius} метров \r\n \r\n"
    for index, point in data.head(min(10, len(data))).iterrows():
        message += f"⚕ [{round(point['distance'], 2)} км] {point['address']} \r\n"

    return map_extension.save_plot(log, data, min_lat, max_lat, min_lon, max_lon,
                                   pt_color='#00EB62FF', pt_size=1000, user_lat=lat, user_lon=lon), message
