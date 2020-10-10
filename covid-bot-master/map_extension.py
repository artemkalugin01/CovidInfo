import matplotlib
import pandas as pd
import matplotlib.pyplot as plt
import geopandas as gp
import contextily as ctx
import shapely.geometry as geometry
import plot_extension
import datetime
matplotlib.use('Agg')


# geo data filter by boundary box
def filter_by_bounding_box(df, min_lat, max_lat, min_lon, max_lon):
    return df[(df['latitude'] > min_lat) &
              (df['latitude'] < max_lat) &
              (df['longitude'] > min_lon) &
              (df['longitude'] < max_lon)]


# get GeoSeries from point dataset
def get_point_series(df):
    lat = df['latitude'].values
    lon = df['longitude'].values

    gdf = gp.GeoSeries([geometry.Point(lon[i], lat[i]) for i in range(len(df))], crs="epsg:4326")
    return gdf.to_crs(epsg=3857)


# get bounds by specific zoom coefficient
def get_bounds(lat, lon, zoom=1):
    min_lat = lat - 0.032 * zoom
    max_lat = lat + 0.032 * zoom

    min_lon = lon - 0.045 * zoom
    max_lon = lon + 0.045 * zoom
    return min_lat, max_lat, min_lon, max_lon


def save_plot(log, df, min_lat, max_lat, min_lon, max_lon, pt_color='#ff000055', pt_size=10000, user_lat=None,
              user_lon=None):
    log.debug('Creating plot')

    # get geo-frame
    bound_df = pd.DataFrame({
        'date': pd.Series([datetime.datetime.now() for i in range(4)]),
        'address': pd.Series([str() for i in range(4)]),
        'latitude': pd.Series([min_lat, min_lat, max_lat, max_lat, user_lat]),
        'longitude': pd.Series([min_lon, max_lon, min_lon, max_lon, user_lon])
    })
    df = df.append(bound_df, ignore_index=True)
    gdf = get_point_series(df)

    # plot points
    colors = [pt_color for i in range(len(gdf))]
    colors[-1] = '#101B1CFF'
    colors[-2] = '#ffffff00'
    colors[-3] = '#ffffff00'
    colors[-4] = '#ffffff00'
    colors[-5] = '#ffffff00'

    sizes = [pt_size for i in range(len(gdf))]
    sizes[-1] = 10000
    sizes[-2] = 1
    sizes[-3] = 1
    sizes[-4] = 1
    sizes[-5] = 1

    ax = gdf.plot(figsize=(30, 30), color=colors, markersize=sizes, marker='o')

    # plot base map
    ctx.add_basemap(ax, source=ctx.providers.Stamen.Toner)

    # save temporary
    ax.set_axis_off()

    # return binary
    return plot_extension.get_binary(plt, log, 'map')
