#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jul  3 13:29:51 2019

@author: shlomi
"""

from strat_startup import *
import pandas as pd
import geopandas as gpd
import numpy as np
sound_path = work_chaim / 'sounding'
igra2 = pd.read_fwf(cwd / 'igra2-station-list.txt', header=None)
igra2.columns = ['station_number', 'lat', 'lon', 'alt', 'name', 'start_year',
                 'end_year', 'number']
igra2 = igra2[igra2['lat'] > -90]
world = gpd.read_file(cwd / 'gis/Countries_WGS84.shp')
geo_igra2 = gpd.GeoDataFrame(igra2, geometry=gpd.points_from_xy(igra2.lon,
                                                                igra2.lat),
                               crs=world.crs)
geo_igra2_eq = geo_igra2[np.abs(geo_igra2['lat'])<10]
geo_igra2_eq = geo_igra2_eq[geo_igra2_eq['end_year'] >= 2017]
geo_igra2_eq = geo_igra2_eq[geo_igra2_eq['start_year'] <= 1993]
ax = world.plot()
geo_igra2_eq.plot(ax=ax, column='alt', cmap='Reds', edgecolor='black',
                     legend=True)


def calc_cold_point_from_sounding(path=sound_path, times=('1991', '2018'),
                                  plot=True):
    import xarray as xr
    import seaborn as sns
    from aux_functions_strat import deseason_xr
    anom_list = []
    for file in path.rglob('*.nc'):
        name = file.as_posix().split('/')[-1].split('.')[0]
        print('proccessing station {}:'.format(name))
        station = xr.open_dataset(file)
        station = station.sel(time=slice(times[0], times[1]))
        cold = station.temperature.where(station.pressure < 130).min(
            dim='point')
        cold = cold.resample(time='MS').mean()
        anom = deseason_xr(cold, how='mean')
        anom.name = name
        anom_list.append(anom)
#        argmin_point = station.temperature.argmin(dim='point').values
#        p_points = []
#        for i, argmin in enumerate(argmin_point):
#            p = station.pressure.sel(point=argmin).isel(time=i).values.item()
#            p_points.append(p)
#        sns.distplot(p_points, bins=100, color='c',
#                     label='pressure_cold_points_' + name)
    ds = xr.merge(anom_list)
    da = ds.to_array(dim='name')
    da.name = 'cold_point_anomalies'
    if plot:
        da.to_dataset(dim='name').to_dataframe().plot(subplots=True)
    return da


def siphon_igra2_to_xarray(station, path=sound_path,
                           fields=['temperature', 'pressure'],
                           times=['1984-01-01', '2019-06-30']):
    from siphon.simplewebservice.igra2 import IGRAUpperAir
    import pandas as pd
    import numpy as np
    import xarray as xr
    dates = pd.to_datetime(times)
    print('getting {} from IGRA2...'.format(station))
    df, header = IGRAUpperAir.request_data(dates, station, derived=True)
    dates = header['date'].values
    print('splicing dataframe and converting to xarray dataset...')
    ds_list = []
    for date in dates:
        dff = df[fields].loc[df['date'] == date]
        # release = dff.iloc[0, 1]
        dss = dff.to_xarray()
        # dss.attrs['release'] = release
        ds_list.append(dss)
    max_ind = np.max([ds.index.size for ds in ds_list])
    vars_ = np.nan * np.ones((len(dates), len(fields), max_ind))
    for i, ds in enumerate(ds_list):
        size = ds[[x for x in ds.data_vars][0]].size
        vars_[i, :, 0:size] = ds.to_array().values
    Vars = xr.DataArray(vars_, dims=['time', 'var', 'point'])
    Vars['time'] = dates
    Vars['var'] = fields
    ds = Vars.to_dataset(dim='var')
    for field in fields:
        ds[field].attrs['units'] = df.units[field]
    print('Done!')
    filename = station + '.nc'
    comp = dict(zlib=True, complevel=9)  # best compression
    encoding = {var: comp for var in ds.data_vars}
    ds.to_netcdf(path / filename, 'w', encoding=encoding)
    print('saved {} to {}.'.format(filename, path))
    return ds


def run_pyigra_save_xarray(station, path=sound_path):
    import subprocess
    command = '/home/ziskin/anaconda3/bin/PyIGRA --id ' + station + ' --parameters TEMPERATURE,PRESSURE -o ' + station + '_pt.txt'
    subprocess.call([command], shell=True)
    pyigra_to_xarray(station + '_pt.txt', path=path)
    return


def pyigra_to_xarray(pyigra_output_filename, path=sound_path):
    import pandas as pd
    import xarray as xr
    import numpy as np
    df = pd.read_csv(sound_path / pyigra_output_filename,
                     delim_whitespace=True)
    dates = df['NOMINAL'].unique().tolist()
    print('splicing dataframe and converting to xarray dataset...')
    ds_list = []
    for date in dates:
        dff = df.loc[df.NOMINAL == date]
        # release = dff.iloc[0, 1]
        dff = dff.drop(['NOMINAL', 'RELEASE'], axis=1)
        dss = dff.to_xarray()
        # dss.attrs['release'] = release
        ds_list.append(dss)
    print('concatenating to time-series dataset')
    datetimes = pd.to_datetime(dates, format='%Y%m%d%H')
    max_ind = np.max([ds.index.size for ds in ds_list])
    T = np.nan * np.ones((len(dates), max_ind))
    P = np.nan * np.ones((len(dates), max_ind))
    for i, ds in enumerate(ds_list):
        tsize = ds['TEMPERATURE'].size
        T[i, 0:tsize] = ds['TEMPERATURE'].values
        P[i, 0:tsize] = ds['PRESSURE'].values
    Tda = xr.DataArray(T, dims=['time', 'point'])
    Tda.name = 'Temperature'
    Tda.attrs['units'] = 'deg C'
    Tda['time'] = datetimes
    Pda = xr.DataArray(P, dims=['time', 'point'])
    Pda.name = 'Pressure'
    Pda.attrs['units'] = 'hPa'
    Pda['time'] = datetimes
    ds = Tda.to_dataset(name='Temperature')
    ds['Pressure'] = Pda
    print('Done!')
    filename = pyigra_output_filename.split('.')[0] + '.nc'
    comp = dict(zlib=True, complevel=9)  # best compression
    encoding = {var: comp for var in ds.data_vars}
    ds.to_netcdf(path / filename, 'w', encoding=encoding)
    print('saved {} to {}.'.format(filename, path))
    return ds


def process_sounding_json(savepath=sound_path, igra_id='BRM00082332'):
    """process json files from sounding download and parse them to xarray"""
    import pandas as pd
    import json
    import xarray as xr
    import os
    # loop over lines lists in each year:
    # pw_years = []
    df_years = []
    bad_line = []
    for file in sorted(savepath.glob(igra_id + '*.json')):
        year = file.as_posix().split('.')[0].split('_')[-1]
        print('Opening station {} json file year: {}'.format(igra_id, year))
        with open(file) as read_file:
            lines_list = json.load(read_file)
        # loop over the lines list:
        # pw_list = []
        dt_list = []
        df_list = []
        for lines in lines_list:
            # print('.')
            try:
                # pw = float([x for x in lines if '[mm]' in x][0].split(':')[-1])
                dt = [x for x in lines if 'Observation time' in
                      x][0].split(':')[-1].split()[0]
                # The %y (as opposed to %Y) is to read 2-digit year
                # (%Y=4-digit)
                header_line = [
                    x for x in range(
                        len(lines)) if 'Observations at'
                    in lines[x]][0] + 3
                end_line = [x for x in range(len(lines)) if
                            'Station information and sounding indices'
                            in lines[x]][0]
                header = lines[header_line].split()
                units = lines[header_line + 1].split()
                with open(savepath/'temp.txt', 'w') as f:
                    for item in lines[header_line + 3: end_line]:
                        f.write("%s\n" % item)
                df = pd.read_fwf(savepath / 'temp.txt', names=header)
                try:
                    os.remove(savepath / 'temp.txt')
                except OSError as e:  # if failed, report it back to the user
                    print("Error: %s - %s." % (e.filename, e.strerror))
#                df = pd.DataFrame(
#                    [x.split() for x in lines[header_line + 3:end_line]],
#                    columns=header)
                df = df.astype(float)
                dt_list.append(pd.to_datetime(dt, format='%y%m%d/%H%M'))
                # pw_list.append(pw)
                df_list.append(df)
                st_num = int([x for x in lines if 'Station number' in
                              x][0].split(':')[-1])
                st_lat = float([x for x in lines if 'Station latitude' in
                                x][0].split(':')[-1])
                st_lon = float([x for x in lines if 'Station longitude' in
                                x][0].split(':')[-1])
                st_alt = float([x for x in lines if 'Station elevation' in
                                x][0].split(':')[-1])
            except IndexError:
                print('no data found in lines entry...')
                bad_line.append(lines)
                continue
            except AssertionError:
                bad_line.append(lines)
            except ValueError:
                bad_line.append(lines)
                continue
        # pw_year = xr.DataArray(pw_list, dims=['time'])
        df_year = [xr.DataArray(x, dims=['mpoint', 'var']) for x in df_list]
        try:
            df_year = xr.concat(df_year, 'time')
            df_year['time'] = dt_list
            df_year['var'] = header
            # pw_year['time'] = dt_list
            # pw_years.append(pw_year)
            df_years.append(df_year)
        except ValueError:
            print('year {} file is bad data or missing...'.format(year))
            continue
        # return df_list, bad_line
    # pw = xr.concat(pw_years, 'time')
    da = xr.concat(df_years, 'time')
    da.attrs['description'] = 'upper air soundings full profile'
    units_dict = dict(zip(header, units))
    for k, v in units_dict.items():
        da.attrs[k] = v
#    pw.attrs['description'] = 'BET_DAGAN soundings of precipatable water'
#    pw.attrs['units'] = 'mm'  # eqv. kg/m^2
    da.attrs['station_number'] = st_num
    da.attrs['station_lat'] = st_lat
    da.attrs['station_lon'] = st_lon
    da.attrs['station_alt'] = st_alt
#    pw = pw.sortby('time')
    da = da.sortby('time')
    # drop 0 pw - not physical
    # pw = pw.where(pw > 0, drop=True)
    # pw.to_netcdf(savepath / 'PW_bet_dagan_soundings.nc', 'w')
    filename = igra_id + '_sounding.nc'
    da.to_netcdf(savepath / filename, 'w')
    return da, bad_line
