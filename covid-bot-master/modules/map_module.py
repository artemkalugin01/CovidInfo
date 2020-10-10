import geopy.distance
import geopy
import pandas as pd
import ssl
import logger
import map_extension

ssl._create_default_https_context = ssl._create_unverified_context
log = logger.get_logger("map_module")


# get content method
def get_content(db_engine, lon=None, lat=None):
    log.info(f"Ambulances map creator started [{lon}][{lat}]")
    zoom = 1.0 / 5

    # read full dataset
    raw_df = pd.read_sql('covid_ambulances', con=db_engine)
    raw_df['distance'] = raw_df.apply(lambda row:
                                      geopy.distance.distance((row['latitude'], row['longitude']), (lat, lon)).km,
                                      axis=1)

    # get data
    min_lat, max_lat, min_lon, max_lon = map_extension.get_bounds(lat, lon, zoom)
    data = map_extension.filter_by_bounding_box(raw_df, min_lat, max_lat, min_lon, max_lon)

    if len(data) > 0:
        log.debug(f'{len(data)} points found')
    else:
        log.debug('Trying to increase bounding box')
        # if points not found, this coef need to be declared by specific value
        step = 0.1
        # searching for points
        while len(data) < 1:
            zoom += step
            min_lat, max_lat, min_lon, max_lon = map_extension.get_bounds(lat, lon, zoom)
            data = map_extension.filter_by_bounding_box(raw_df, min_lat, max_lat, min_lon, max_lon)
        log.debug(f'{len(data)} points found')

    data = data.sort_values(by=['distance'])
    message = f"По данным портала MASH вокруг вас найдено {len(data)} мест вызовов скорых по коду COVID \r\n \r\n"
    for index, point in data.head(min(10, len(data))).iterrows():
        message += f"🦠 [{round(point['distance'], 2)} км] {point['address']} \r\n"

    return map_extension.save_plot(log, data, min_lat, max_lat, min_lon, max_lon,
                                   user_lat=lat, user_lon=lon), message
