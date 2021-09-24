# Boilerplate code for GPS parsing

# Standard imports:
import matplotlib.pyplot as plt
import matplotlib
matplotlib.rc('image', aspect='auto', interpolation='nearest')
import numpy as np
import pandas as pd
from collections import OrderedDict
import json
import glob
import types
import os

# Geodata libraries:
from shapely.geometry import Point
import geopandas
import contextily as ctx

# VEDB libraries:
import vedb_store
from vedb_store.utils import parse_sensorstream_gps
import file_io

def _get_min_max(gdf, sc=4):
    mn_long, mn_lat = np.min(np.array([[g.bounds[0], g.bounds[1]] for g in gdf['geometry']]), axis=0)
    mx_long, mx_lat = np.max(np.array([[g.bounds[0], g.bounds[1]] for g in gdf['geometry']]), axis=0)
    lat_range = mx_lat - mn_lat
    long_range = mx_long - mn_long
    ylim = (mn_lat - sc * lat_range, mx_lat + sc * lat_range)
    xlim = (mn_long - sc * long_range, mx_long + sc * long_range)
    return xlim, ylim

def convert_to_points(data):
    """Convert loaded data to geopandas dataframe depicting points"""
    if not isinstance(data, types.SimpleNamespace):
        data = types.SimpleNamespace(**data)

    df = pd.DataFrame(data=dict(Latitude=data.gps_lat,
                                    Longitude=data.gps_lon,
                                    ))
    geometry = [Point(xy) for xy in zip(df['Longitude'], df['Latitude'])]
    geo_df_latlong = geopandas.GeoDataFrame(df, crs='EPSG:4326', geometry=geometry)
    geo_df_wm = geo_df_latlong.to_crs(epsg=3857)
    return geo_df_wm
    

def plot_on_map(latlon_data, geo_shape, ax=None, set_min_max=False):
    """Plot latitude & longitude data on a map
    """
    if not isinstance(latlon_data, types.SimpleNamespace):
        latlon_data = types.SimpleNamespace(**latlon_data)
    if geo_shape.crs.to_epsg() != 3857:
        geo_shape = geo_shape.to_crs(epsg=3857)

    # Convert latitude / longitude to shape data
    df = pd.DataFrame(data=dict(Latitude=latlon_data.gps_lat,
                                    Longitude=latlon_data.gps_lon,
                                    ))
    geometry = [Point(xy) for xy in zip(df['Longitude'], df['Latitude'])]
    geo_df_latlong = geopandas.GeoDataFrame(df, crs='EPSG:4326', geometry=geometry)
    geo_df_web = geo_df_latlong.to_crs(epsg=3857)


    if ax is None:
        fig, ax = plt.subplots()
    else:
        fig = ax.get_figure()
    #geo_shape.plot(ax=ax, alpha=0.5, edgecolor='k')
    # Better to make this a line vs a set of points; whatever.
    geo_df_web.plot(ax=ax, color='r')
    if set_min_max:
        # This doesn't seem to work. Need to figure out how to zoom.
        xlim, ylim = _get_min_max(geo_df_web, sc=0.5)
        ax.set_xlim(xlim)
        ax.set_ylim(ylim)
        fig.canvas.draw()
        fig.canvas.flush_events()
        ax.axis('equal')
        fig.canvas.draw()
        fig.canvas.flush_events()
    ctx.add_basemap(ax, source=ctx.sources.OSM_A)



