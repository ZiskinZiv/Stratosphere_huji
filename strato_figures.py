#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jan 10 10:26:13 2020

@author: shlomi
"""

from strat_paths import work_chaim
from matplotlib import rcParams
import matplotlib.pyplot as plt
from matplotlib.ticker import ScalarFormatter
import matplotlib.dates as mdates
import seaborn as sns
import matplotlib.ticker as mticker
from palettable.scientific import sequential as seqsci
from palettable.colorbrewer import sequential as seqbr
from palettable.scientific import diverging as divsci
from palettable.colorbrewer import diverging as divbr
from matplotlib.colors import ListedColormap
from cartopy.mpl.ticker import LongitudeFormatter, LatitudeFormatter
import matplotlib.ticker as ticker
from pathlib import Path
from strat_paths import savefig_path

error_cmap = seqsci.Nuuk_11.mpl_colormap
error_cmap = seqbr.YlGnBu_9.mpl_colormap
# predict_cmap = ListedColormap(divbr.BrBG_11.mpl_colors)
predict_cmap = divsci.Vik_20.mpl_colormap
# predict_cmap = ListedColormap(divsci.Vik_20.mpl_colors)
rc = {
    'font.family': 'serif',
    'xtick.labelsize': 'medium',
    'ytick.labelsize': 'medium'}
for key, val in rc.items():
    rcParams[key] = val
sns.set(rc=rc, style='ticks')
fields_dict = {'r2_adj': r'Adjusted R$^2$', 'params': r'$\beta$ coeffs'}


def add_horizontal_colorbar(fg_obj, rect=[0.1, 0.1, 0.8, 0.025], cbar_kwargs_dict=None):
    # rect = [left, bottom, width, height]
    # add option for just figure object, now, accepts facetgrid object only
    cbar_kws = {'label': '', 'format': '%0.2f'}
    if cbar_kwargs_dict is not None:
        cbar_kws.update(cbar_kwargs_dict)
    cbar_ax = fg_obj.fig.add_axes(rect)
    fg_obj.add_colorbar(cax=cbar_ax, orientation="horizontal", **cbar_kws)
    return fg_obj


def parse_quantile(rds, quan):
    vals = rds.quantile(quan)
    vals = [abs(x) for x in vals]
    if vals[0] < vals[1]:
        quan_kws = {'vmin': -vals[0]}
    else:
        quan_kws = {'vmax': vals[1]}
    return quan_kws


def plot_forecast_busts_lines(ax, color='r', style='--'):
    # three forecast busts:
    # 2010D2011JFM, 2015-OND, 2016-OND
    # ax.axvline('2010-05', c=color, ls=style)
    # ax.axvline('2010-09', c=color, ls=style)
    ax.axvline('2010-11', c=color, ls=style)
    # ax.axvline('2010-12', c=color, ls=style)
    ax.axvline('2011-04', c=color, ls=style)
    ax.axvline('2015-09', c=color, ls=style)
    ax.axvline('2016-01', c=color, ls=style)
    ax.axvline('2016-09', c=color, ls=style)
    ax.axvline('2017-01', c=color, ls=style)
    return ax


#def add_season_equals(ax):
#    if ax.texts:
#        # This contains the right ylabel text
#        txt = ax.texts[0]
#        label = txt.get_text()
#        label = 'season = {}'.format(label)
#        ax.text(txt.get_unitless_position()[0], txt.get_unitless_position()[1],
#                label,
#                transform=ax.transAxes,
#                va='center',
#                # fontsize='xx-large',
#                rotation=-90)
#        # Remove the original text
#        ax.texts[0].remove()
#    return ax


def remove_time_and_set_date(ax):
    if ax.texts:
    # This contains the right ylabel text
        txt = ax.texts[0]
        label = txt.get_text()
        label = '-'.join(label.split('=')[-1].strip(' ').split('-')[0:2])
        ax.text(txt.get_unitless_position()[0], txt.get_unitless_position()[1],
                label,
                transform=ax.transAxes,
                va='center',
                # fontsize='xx-large',
                rotation=-90)
        # Remove the original text
        ax.texts[0].remove()
    return ax


def remove_anomaly_and_set_title(ax, species='H2O'):
    if species == 'H2O':
        original = 'Combined water vapor'
    elif species == 't':
        original = 'Air temperature'
    elif species == 'u':
        original = 'Zonal wind'
    short_titles = {'original': '{} anomaly'.format(original),
                    'predict': 'MLR reconstruction',
                    'resid': 'Residuals'}
    title = ax.get_title()
    title = title.split('=')[-1].strip(' ')
    title = short_titles.get(title)
    ax.set_title(title)
    return ax


def remove_regressors_and_set_title(ax, set_title_only=None):
    short_titles = {'qbo_cdas': 'QBO',
                    'anom_nino3p4': 'ENSO',
                    'ch4': 'CH4',
                    'era5_bdc': 'BDC',
                    'era5_t500': 'T at 500hPa',
                    'anom_nino3p4^2': r'ENSO$^2$',
                    'anom_nino3p4*q...': r'ENSO $\times$ QBO'}
    title = ax.get_title()
    title = title.split('=')[-1].strip(' ')
    if set_title_only is not None:
        title = short_titles.get(set_title_only)
    else:
        title = short_titles.get(title)
    ax.set_title(title)
    return ax


@ticker.FuncFormatter
def lon_formatter(x, pos):
    if x < 0:
        return r'{0:.0f}$\degree$W'.format(abs(x))
    elif x > 0:
        return r'{0:.0f}$\degree$E'.format(abs(x))
    elif x == 0:
        return r'0$\degree$'

@ticker.FuncFormatter
def lat_formatter(x, pos):
    if x < 0:
        return r'{0:.0f}$\degree$S'.format(abs(x))
    elif x > 0:
        return r'{0:.0f}$\degree$N'.format(abs(x))
    elif x == 0:
        return r'0$\degree$'


@ticker.FuncFormatter
def single_digit_formatter(x, pos):
    return '{0:.0f}'.format(x)


def change_xticks_years(ax, start=1984, end=2018):
    import pandas as pd
    import numpy as np
    years_fmt = mdates.DateFormatter('%Y')
    years = np.arange(start, end + 1, 1)
    years = [pd.to_datetime(str(x)).strftime('%Y') for x in years]
    ax.set_xticks(years)
    # ax.xaxis.set_major_locator(mdates.YearLocator())
    ax.xaxis.set_major_formatter(years_fmt)
    return ax


def plot_figure_1(path=work_chaim, regressors=['qbo_cdas']):
    from ML_OOP_stratosphere_gases import run_ML
    # sns.set_style('ticks', rc=rc)
    cbar_kws = {'label': '', 'format': '%0.2f', 'aspect': 50}
    if len(regressors) == 1:
        rds = run_ML(time_period=['1984', '2019'], regressors=regressors,
                     special_run={'optimize_reg_shift': [0, 12]},
                     area_mean=True, lat_slice=[-20, 20])
        fg = rds.r2_adj.T.plot.pcolormesh(yscale='log', yincrease=False,
                                          levels=21, col='reg_shifted',
                                          cmap=error_cmap, extend=None,
                                          figsize=(7, 7),
                                          cbar_kwargs=cbar_kws)
        ax = fg.axes[0][0]
        ax.yaxis.set_major_formatter(ScalarFormatter())

        rds.isel(reg_shifted=0).level_month_shift.plot.line('r.-', y='level',
                                                            yincrease=False,
                                                            ax=ax)
        ax.set_xlabel('lag [months]')
        ax.set_title('')
        fg.fig.tight_layout()
        fg.fig.subplots_adjust(right=0.8)
        print('Caption:')
        print('The adjusted R^2 for the QBO index from CDAS as a function of pressure level and month lag. The solid line and dots represent the maximum R^2 for each pressure level.')
        filename = 'r2_{}_shift_optimize.png'.format(regressors[0])
    else:
        rds = run_ML(time_period=['1984', '2018'], regressors=regressors,
                     special_run={'optimize_reg_shift': [0, 12]},
                     area_mean=True, lat_slice=[-20, 20])
        fg = rds.r2_adj.T.plot.pcolormesh(yscale='log', yincrease=False,
                                          levels=21, col='reg_shifted',
                                          cmap=error_cmap, vmin=0.0,
                                          extend='both', figsize=(13, 4),
                                          add_colorbar=False)
        cbar_kws = {'label': '', 'format': '%0.2f'}
        cbar_ax = fg.fig.add_axes([0.1, 0.1, .8, .025])
        fg.add_colorbar(cax=cbar_ax, orientation="horizontal", **cbar_kws)
        for n_regs in range(len(fg.axes[0])):
            rds.isel(reg_shifted=n_regs).level_month_shift.plot.line('r.-',
                                                                     y='level',
                                                                     yincrease=False,
                                                                     ax=fg.axes[0][n_regs])
        for ax in fg.axes.flatten():
            ax.set_xlabel('lag [months]')
            ax = remove_regressors_and_set_title(ax)
            ax.yaxis.set_major_formatter(ScalarFormatter())
            ax.set_ylabel('')
        fg.axes[0][0].set_ylabel('Pressure [hPa]')
        fg.fig.tight_layout()
        fg.fig.subplots_adjust(left=0.07, bottom=0.27)
        print('Caption:')
        print('The adjusted R^2 for the QBO, BDC and T500 predictors as a function of pressure level and month lag. The solid line and dots represent the maximum R^2 for each pressure level.')
        filename = 'r2_{}_shift_optimize.png'.format(
            '_'.join([x for x in regressors]))
    plt.savefig(savefig_path / filename, bbox_inches='tight')
    return fg


def plot_figure_2(path=work_chaim, robust=False):
    from ML_OOP_stratosphere_gases import plot_like_results
    import xarray as xr
    rds = xr.open_dataset(
        path /
        'MLR_H2O_latpress_cdas-plags_ch4_enso_1984-2019.nc')
    fg = plot_like_results(rds, plot_key='predict_level-time', lat=None,
                           cmap=predict_cmap, robust=robust, extend=None,
                           no_colorbar=True)
    top_ax = fg.axes[0][0]
    mid_ax = fg.axes[1][0]
    bottom_ax = fg.axes[-1][0]
    # remove time from xlabel:
    bottom_ax.set_xlabel('')
    # new ticks:
    bottom_ax = change_xticks_years(bottom_ax, start=1985, end=2019)
    top_ax.set_title(
        r'Area-averaged (weighted by cosine of latitudes 60$\degree$S to 60$\degree$N) combined water vapor anomaly')
    mid_ax.set_title('MLR reconstruction')
    bottom_ax.set_title('Residuals')
    [ax.yaxis.set_major_formatter(single_digit_formatter)
     for ax in [top_ax, mid_ax, bottom_ax]]
    fg = add_horizontal_colorbar(fg, [0.125, 0.057, 0.8, 0.02],
                                 cbar_kwargs_dict={'label': 'ppmv'})
    fg.fig.tight_layout()
    fg.fig.subplots_adjust(left=0.06, bottom=0.14)
    print('Caption: ')
    print('Stratospheric water vapor anomalies and their MLR reconstruction and residuals, spanning from 1984 to 2018 and using CH4, ENSO and pressure level lag varied QBO as predictors')
    filename = 'MLR_H2O_predict_level-time_cdas-plags_ch4_enso.png'
    plt.savefig(savefig_path / filename, bbox_inches='tight')
    return fg


def plot_figure_3(path=work_chaim):
    from ML_OOP_stratosphere_gases import plot_like_results
    import xarray as xr
    rds = xr.open_dataset(
        path /
        'MLR_H2O_latpress_cdas-plags_ch4_enso_1984-2019.nc')
    fg = plot_like_results(rds, plot_key='r2_level-lat', cmap=error_cmap,
                           extend=None, add_colorbar=True)
    fg.ax.set_title('')
    fg.ax.xaxis.set_major_formatter(lat_formatter)
    fg.ax.yaxis.set_major_formatter(single_digit_formatter)
    fg.ax.figure.tight_layout()
    fg.ax.figure.subplots_adjust(left=0.15, right=1.0, bottom=0.05, )
    fg.ax.set_xlabel('')
    print('Caption: ')
    print('The adjusted R^2 for the water vapor MLR analysis(1984-2018) with CH4, ENSO and pressure level lag varied QBO as predictors')
    filename = 'MLR_H2O_r2_level-lat_cdas-plags_ch4_enso.png'
    plt.savefig(savefig_path / filename, bbox_inches='tight')
    return fg


def plot_figure_4(path=work_chaim):
    from ML_OOP_stratosphere_gases import plot_like_results
    import xarray as xr
    rds = xr.open_dataset(
        path /
        'MLR_H2O_latpress_cdas-plags_ch4_enso_1984-2019.nc')
    fg = plot_like_results(rds, plot_key='params_level-lat', cmap=predict_cmap,
                           figsize=(10, 5), extend=None, no_colorbar=True)
    fg.fig.suptitle('')
    fg.fig.canvas.draw()
    for ax in fg.axes.flatten():
        ax.yaxis.set_major_formatter(single_digit_formatter)
        ax.xaxis.set_major_formatter(lat_formatter)
        ax.set_xlabel('')
        ax = remove_regressors_and_set_title(ax)
        
    fg = add_horizontal_colorbar(fg, [0.125, 0.1, 0.8, 0.02],
                                 cbar_kwargs_dict={'label': ''})
    fg.fig.tight_layout()
    fg.fig.subplots_adjust(left=0.1, bottom=0.21)
    print('Caption: ')
    print('The beta coefficiants for the water vapor MLR analysis(1984-2018) with CH4, ENSO and pressure level lag varied QBO as predictors')
    filename = 'MLR_H2O_params_level-lat_cdas-plags_ch4_enso.png'
    plt.savefig(savefig_path / filename, bbox_inches='tight')
    return fg


def plot_latlon_predict(ncfile, path=work_chaim, geo='lat', level=82.54,
                        bust_lines=True, save=True):
    from ML_OOP_stratosphere_gases import plot_like_results
    import xarray as xr
    import math
    rds = xr.open_dataset(path / ncfile)
    species = ncfile.split('.')[0].split('_')[1]
    regs = '_'.join(ncfile.split('.')[0].split('_')[3: -1])
    if species == 'H2O':
        geo_title = {
                'lat': r'Area-averaged (from 180$\degree$W to 180$\degree$E longitudes) combined H2O anomaly for the {} hPa pressure level'.format(level),
                'lon': r'Area-averaged (weighted by cosine of latitudes 60$\degree$S to 60$\degree$N) combined H2O anomaly for the {} hPa pressure level'.format(level)}
        st_year = 2005
        unit = 'ppmv'
    elif species == 't':
        geo_title = {
                'lat': r'Area-averaged (from 180$\degree$W to 180$\degree$E longitudes) air temperature anomaly for the {} hPa pressure level'.format(level),
                'lon': r'Area-averaged (weighted by cosine of latitudes 60$\degree$S to 60$\degree$N) air temperature anomaly for the {} hPa pressure level'.format(level)}
        st_year = 1984
        unit = 'K'
    elif species == 'u':
        geo_title = {
                'lat': r'Area-averaged (from 180$\degree$W to 180$\degree$E longitudes) zonal wind anomaly for the {} hPa pressure level'.format(level),
                'lon': r'Area-averaged (weighted by cosine of latitudes 60$\degree$S to 60$\degree$N) zonal wind anomaly for the {} hPa pressure level'.format(level)}
        st_year = 1984
        unit = r'm$\cdot$sec$^{-1}$'
    fg = plot_like_results(rds, plot_key='predict_{}-time'.format(geo),
                           level=level, cmap=predict_cmap, extend=None,
                           no_colorbar=True)
    top_ax = fg.axes[0][0]
    mid_ax = fg.axes[1][0]
    bottom_ax = fg.axes[-1][0]
    # remove time from xlabel:
    bottom_ax.set_xlabel('')
    # new ticks:
    bottom_ax = change_xticks_years(bottom_ax, start=st_year, end=2019)
    top_ax.set_title(geo_title.get(geo))
    mid_ax.set_title('MLR reconstruction')
    bottom_ax.set_title('Residuals')
    # fg.fig.canvas.draw()
    for ax in [top_ax, mid_ax, bottom_ax]:
        if geo == 'lon':
            ax.yaxis.set_major_formatter(lon_formatter)
        elif geo == 'lat':
            ax.yaxis.set_major_formatter(lat_formatter)
        ax.set_ylabel('')
        if bust_lines:
            ax = plot_forecast_busts_lines(ax, color='k')
    fg = add_horizontal_colorbar(fg, [0.1, 0.065, 0.8, 0.015],
                             cbar_kwargs_dict={'label': unit})
    fg.fig.tight_layout()
    fg.fig.subplots_adjust(left=0.05, bottom=0.14)
    if save:
        filename = 'MLR_{}_predict_{}-time_{}_{}_{}-2019.png'.format(species, geo, math.floor(level), regs, st_year)
        fg.fig.savefig(savefig_path / filename , bbox_inches='tight')
    return fg


def plot_figure_5(path=work_chaim):
    ncfile = 'MLR_H2O_latlon_cdas-plags_ch4_enso_2004-2019.nc'
    fg = plot_latlon_predict(ncfile, path=path, geo='lat', level=82.54,
                             bust_lines=True, save=True)
    print('Caption: ')
    print('The zonal mean water vapor anomalies for the 82.54 hPa level and their MLR reconstruction and residuals, spanning from 2004 to 2018. This MLR analysis was carried out with CH4 ,ENSO and pressure level lag varied QBO as predictors. Note the three forecast "busts": 2010-D to 2011-JFM, 2015-OND and 2016-OND')
    return fg


def plot_figure_6(path=work_chaim):
    ncfile = 'MLR_H2O_latlon_cdas-plags_ch4_enso_2004-2019.nc'
    fg = plot_latlon_predict(ncfile, path=path, geo='lon', level=82.54,
                             bust_lines=True, save=True)
    print('Caption: ')
    print('The meridional mean water vapor anomalies for the 82.54 hPa level and their MLR reconstruction and residuals, spanning from 2004 to 2018. This MLR analysis was carried out with CH4 ,ENSO and pressure level lag varied QBO as predictors. Note the three forecast "busts": 2010-D to 2011-JFM, 2015-OND and 2016-OND')
    return fg


def plot_figure_seasons(ncfile, path=work_chaim, field='params'):
    import xarray as xr
    rds = xr.open_dataset(path / ncfile)
    species = ncfile.split('.')[0].split('_')[1]
    if species == 'H2O':
        unit = 'ppmv'
    elif species == 't':
        unit = 'K'
    elif species == 'u':
        unit = r'm$\cdot$sec$^{-1}$'
    if field == 'params':
        unit = ''
    regs = '_'.join(ncfile.split('.')[0].split('_')[3: -1])
    syear = ncfile.split('.')[0].split('_')[-1].split('-')[0]
    eyear = ncfile.split('.')[0].split('_')[-1].split('-')[-1]
    rds = rds.sortby('season')
    plt_kwargs = {'cmap': predict_cmap, 'figsize': (15, 10),
                  'add_colorbar': False,
                  'extend': None, 'yscale': 'log',
                  'yincrease': False, 'center': 0.0, 'levels': 41}
    data = rds[field]
    fg = data.plot.contourf(
        col='regressors', row='season', **plt_kwargs)
    fg = add_horizontal_colorbar(fg, [0.1, 0.065, 0.8, 0.015], cbar_kwargs_dict={'label': unit})
    fg.fig.subplots_adjust(bottom=0.13, top=0.95, left=0.06)
    [ax.invert_yaxis() for ax in fg.axes.flat]
    [ax.yaxis.set_major_formatter(ScalarFormatter()) for ax in fg.axes.flat]
    [ax.yaxis.set_major_formatter(single_digit_formatter)
     for ax in fg.axes.flat]
    for top_ax in fg.axes[0]:
        remove_regressors_and_set_title(top_ax)
    fg.fig.canvas.draw()
    for bottom_ax in fg.axes[-1]:
        bottom_ax.xaxis.set_major_formatter(lat_formatter)
        bottom_ax.set_xlabel('')
    filename = 'MLR_{}_params_level-lat_{}_{}-{}.png'.format(species, regs, syear, eyear)
    plt.savefig(savefig_path / filename, bbox_inches='tight')
    return fg


def plot_figure_7(path=work_chaim):
    ncfile = 'MLR_H2O_latpress_seasons_cdas-plags_ch4_enso_1984-2019.nc'
    fg = plot_figure_seasons(ncfile, path, field='params')
    print('Caption: ')
    print('The beta coefficients for the water vapor MLR season analysis for pressure levels vs. latitude with  CH4, ENSO  pressure level lag varied QBO as predictors. This MLR analysis spanned from 1984 to 2018. Note that ENSO is dominant in the MAM season')  
    return fg


def plot_figure_8(path=work_chaim):
    ncfile = 'MLR_H2O_latlon_cdas-plags_ch4_enso_radio_cold_lags6_2004-2019.nc'
    fg = plot_latlon_predict(ncfile, path=path, geo='lat', level=82.54,
                             bust_lines=True, save=True)
    print('Caption: ')
    print('The zonal mean water vapor anomalies for the 82.54 hPa level and their MLR reconstruction and residuals, spanning from 2004 to 2018. This MLR analysis was carried out with CH4 ,ENSO, radio cpt with 6 months lags and pressure level lag varied QBO as predictors. Note that the radio cpt predictor and its 6 lags were able to deal with the forecast busts succsesfully')
    return fg


def plot_figure_9(path=work_chaim):
    ncfile = 'MLR_H2O_latlon_cdas-plags_ch4_enso_radio_cold_lags6_2004-2019.nc'
    fg = plot_latlon_predict(ncfile, path=path, geo='lon', level=82.54,
                             bust_lines=True, save=True)
    print('Caption: ')
    print('The meridional mean water vapor anomalies for the 82.54 hPa level and their MLR reconstruction and residuals, spanning from 2004 to 2018. This MLR analysis was carried out with CH4 ,ENSO, radio cpt with 6 months lags and pressure level lag varied QBO as predictors. Note that the radio cpt predictor and its 6 lags were able to deal with the forecast busts succsesfully')
    return fg


def plot_figure_10(path=work_chaim):
    ncfile = 'MLR_H2O_latlon_cdas-plags_ch4_enso_bdc_t500_2004-2019.nc'
    fg = plot_latlon_predict(ncfile, path=path, geo='lat', level=82.54,
                             bust_lines=True, save=True)
    print('Caption: ')
    print('The zonal mean water vapor anomalies for the 82.54 hPa level and their MLR reconstruction and residuals, spanning from 2004 to 2018. This MLR analysis was carried out with CH4 ,ENSO, BDC, T500 and pressure level lag varied QBO as predictors. Note that T500 and BDC predictors were not able to deal with the forecast busts')
    return fg


def plot_figure_11(path=work_chaim):
    ncfile = 'MLR_H2O_latlon_cdas-plags_ch4_enso_bdc_t500_2004-2019.nc'
    fg = plot_latlon_predict(ncfile, path=path, geo='lon', level=82.54,
                             bust_lines=True, save=True)
    print('Caption: ')
    print('The merdional mean water vapor anomalies for the 82.54 hPa level and their MLR reconstruction and residuals, spanning from 2004 to 2018. This MLR analysis was carried out with CH4 ,ENSO, BDC, T500 and pressure level lag varied QBO as predictors. Note that T500 and BDC predictors were not able to deal with the forecast busts')
    return fg


def plot_figure_12(path=work_chaim, rds=None, save=True):
    """r2 map (lat-lon) for cdas-plags, enso, ch4"""
    import xarray as xr
    import cartopy.crs as ccrs
    import numpy as np
    from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER
    if rds is None:
        rds = xr.open_dataset(
                path /
                'MLR_H2O_latlon_cdas-plags_ch4_enso_2004-2019.nc')
    rds = rds['r2_adj'].sel(level=82, method='nearest')
    fig = plt.figure(figsize=(11, 5))
    ax = fig.add_subplot(1, 1, 1,
                         projection=ccrs.PlateCarree(central_longitude=0))
    ax.coastlines()
    fg = rds.plot.contourf(ax=ax, add_colorbar=False, cmap=error_cmap,
                           vmin=0.0, extend=None, levels=21)
    ax.set_title('')
#    lons = rds.lon.values[0:int(len(rds.lon.values) / 2)][::2]
#    lons_mirror = abs(lons[::-1])
#    lons = np.concatenate([lons, lons_mirror])
#    lats = rds.lat.values[0:int(len(rds.lat.values) / 2)][::2]
#    lats_mirror = abs(lats[::-1])
#    lats = np.concatenate([lats, lats_mirror])
    # ax.set_xticks(lons, crs=ccrs.PlateCarree())
    # ax.set_yticks(lats, crs=ccrs.PlateCarree())
    # lon_formatter = LongitudeFormatter(zero_direction_label=True)
    # lat_formatter = LatitudeFormatter()
    # ax.xaxis.set_major_formatter(lon_formatter)
    # ax.yaxis.set_major_formatter(lat_formatter)
    cbar_kws = {'label': '', 'format': '%0.2f'}
    cbar_ax = fg.ax.figure.add_axes([0.1, 0.1, .8, .035])
    plt.colorbar(fg, cax=cbar_ax, orientation="horizontal", **cbar_kws)
    gl = ax.gridlines(
        crs=ccrs.PlateCarree(),
        linewidth=1,
        color='black',
        alpha=0.5,
        linestyle='--',
        draw_labels=True)
    gl.xlines = True
    gl.xlocator = mticker.FixedLocator([-180, -120, -60, 0, 60, 120, 180])
    gl.ylocator = mticker.FixedLocator([-45, -30, -15, 0, 15, 30 ,45])
    gl.xlabel_style = {'size': 10}
    gl.ylabel_style = {'size': 10}
    gl.xformatter = LONGITUDE_FORMATTER
    gl.yformatter = LATITUDE_FORMATTER
    fig.tight_layout()
    fig.subplots_adjust(top=0.98,left=0.06, right=0.94)
    print('Caption: ')
    print('The adjusted R^2 for the water vapor anomalies MLR analysis in the 82 hPa level with CH4 ,ENSO, and pressure level lag varied QBO as predictors. This MLR spans from 2004 to 2018')
    filename = 'MLR_H2O_r2_map_82_cdas-plags_ch4_enso.png'
    if save:
        plt.savefig(savefig_path / filename, bbox_inches='tight')
    return fg


def plot_feature_map(ncfile, path=work_chaim, rds=None, feature='params',
                     level=82, col_wrap=3, figsize=(17, 3), extent=[-170, 170, -57.5, 57.5]):
    import xarray as xr
    import cartopy.crs as ccrs
    from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER
    if rds is None:
        species = ncfile.split('.')[0].split('_')[1]
        regs = '_'.join(ncfile.split('.')[0].split('_')[3: -1])
        rds = xr.load_dataset(path / ncfile)
    else:
        species = ''
        regs = ''
    rds = rds[feature].sel(level=level, method='nearest')
    proj = ccrs.PlateCarree(central_longitude=0)
    gl_list = []
    fg = rds.plot.contourf(col='regressors', add_colorbar=False,
                           col_wrap=col_wrap,
                           cmap=predict_cmap, center=0.0, extend=None,
                           levels=41, subplot_kws=dict(projection=proj),
                           transform=ccrs.PlateCarree(), figsize=figsize)
    cbar_kws = {'label': '', 'format': '%0.2f'}
    cbar_ax = fg.fig.add_axes([0.1, 0.1, .8, .035])  # last num controls width
    fg.add_colorbar(cax=cbar_ax, orientation="horizontal", **cbar_kws)
    for ax in fg.axes.flatten():
        ax.coastlines()
        ax.set_extent(extent, crs=ccrs.PlateCarree())
        gl = ax.gridlines(
            crs=ccrs.PlateCarree(),
            linewidth=1,
            color='black',
            alpha=0.5,
            linestyle='--',
            draw_labels=True)
        gl.xlabels_top = False
        gl.xlabel_style = {'size': 9}
        gl.ylabel_style = {'size': 9}
        gl.xlines = True
        gl.xlocator = mticker.FixedLocator([-180, -120, -60, 0, 60, 120, 180])
        gl.ylocator = mticker.FixedLocator([-45, -30, -15, 0, 15, 30, 45])
        gl.xformatter = LONGITUDE_FORMATTER
        gl.yformatter = LATITUDE_FORMATTER
        gl_list.append(gl)
        ax = remove_regressors_and_set_title(ax)
    gl_list[0].ylabels_right = False
    gl_list[2].ylabels_left = False
    try:
        gl_list[3].ylabels_right = False
    except IndexError:
        pass
    fg.fig.tight_layout()
    fg.fig.subplots_adjust(right=0.96, left=0.04, wspace=0.15)
#    print('Caption: ')
#    print('The beta coeffciants for the water vapor anomalies MLR analysis in the 82 hPa level at 2004 to 2018')
    filename = 'MLR_{}_{}_map_{}_{}.png'.format(species, feature, level, regs)
    plt.savefig(savefig_path / filename, bbox_inches='tight')
    return fg


def plot_figure_13(path=work_chaim):
    ncfile = 'MLR_H2O_latlon_cdas-plags_ch4_enso_2004-2019.nc'
    fg = plot_feature_map(ncfile, path=path, feature='params', level=82)
    return fg


#def plot_figure_13(path=work_chaim, rds=None, save=True):
#    """params map (lat-lon) for cdas-plags, enso, ch4"""
#    import xarray as xr
#    import cartopy.crs as ccrs
#    from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER
#    if rds is None:
#        rds = xr.open_dataset(
#            path /
#            'MLR_H2O_latlon_cdas-plags_ch4_enso_2004-2019.nc')
#    rds = rds['params'].sel(level=82, method='nearest')
#    proj = ccrs.PlateCarree(central_longitude=0)
##    fig, axes = plt.subplots(1, 3, figsize=(17, 3.0),
##                             subplot_kw=dict(projection=proj))
#    gl_list = []
#    fg = rds.plot.contourf(col='regressors', add_colorbar=False,
#                           cmap=predict_cmap, center=0.0, extend=None,
#                           levels=41, subplot_kws=dict(projection=proj),
#                           transform=ccrs.PlateCarree(), figsize=(17, 3))
#    cbar_kws = {'label': '', 'format': '%0.2f'}
#    cbar_ax = fg.fig.add_axes([0.1, 0.1, .8, .035])  # last num controls width
#    fg.add_colorbar(cax=cbar_ax, orientation="horizontal", **cbar_kws)
#    for ax in fg.axes.flatten():
#        ax.coastlines()
#        gl = ax.gridlines(
#            crs=ccrs.PlateCarree(),
#            linewidth=1,
#            color='black',
#            alpha=0.5,
#            linestyle='--',
#            draw_labels=True)
#        gl.xlabels_top = False
#        gl.xlabel_style = {'size': 9}
#        gl.ylabel_style = {'size': 9}
#        gl.xlines = True
#        gl.xlocator = mticker.FixedLocator([-180, -120, -60, 0, 60, 120, 180])
#        gl.ylocator = mticker.FixedLocator([-45, -30, -15, 0, 15, 30, 45])
#        gl.xformatter = LONGITUDE_FORMATTER
#        gl.yformatter = LATITUDE_FORMATTER
#        gl_list.append(gl)
#        ax = remove_regressors_and_set_title(ax)
#    gl_list[0].ylabels_right = False
#    gl_list[2].ylabels_left = False
#    fg.fig.tight_layout()
#    fg.fig.subplots_adjust(right=0.96, left=0.04, wspace=0.15)
#    print('Caption: ')
#    print('The beta coeffciants for the water vapor anomalies MLR analysis in the 82 hPa level at 2004 to 2018')
#    filename = 'MLR_H2O_params_map_82_cdas-plags_ch4_enso.png'
#    if save:
#        plt.savefig(savefig_path / filename, bbox_inches='tight')
#    return fg


def plot_figure_seasons_map(path=work_chaim, rds=None, field='r2_adj', level=82,
                            save=True, add_to_suptitle=None):
    import xarray as xr
    import cartopy.crs as ccrs
    if field == 'r2_adj':
        cmap = error_cmap
        center = None
        vmin = 0.0
        col = 'season'
        row = None
        figsize = (17, 3)
    elif field == 'params':
        cmap = predict_cmap
        vmin = None
        center = 0.0
        col = 'regressors'
        row = 'season'
        figsize = (17, 17)
    proj = ccrs.PlateCarree(central_longitude=0)
    if rds is None:
        rds = xr.open_dataset(
            path /
            '')
    rds = rds[field].sel(level=level, method='nearest')
    fg = rds.plot.contourf(col=col, row=row, add_colorbar=False,
                           cmap=cmap, center=center, vmin=vmin, extend=None,
                           levels=41, subplot_kws=dict(projection=proj),
                           transform=ccrs.PlateCarree(), figsize=figsize)
    fg = add_horizontal_colorbar(fg, rect=[0.1, 0.1, 0.8, 0.025],
                                 cbar_kwargs_dict=None)
    [ax.coastlines() for ax in fg.axes.flatten()]
    [ax.gridlines(
        crs=ccrs.PlateCarree(),
        linewidth=1,
        color='black',
        alpha=0.5,
        linestyle='--',
        draw_labels=False) for ax in fg.axes.flatten()]
    filename = 'MLR_H2O_{}_map_{}_cdas-plags_ch4_enso_seasons.png'.format(
        field, level)
    sup = '{} for the {} hPa level'.format(fields_dict[field], level)
    if add_to_suptitle is not None:
        sup += add_to_suptitle
    fg.fig.suptitle(sup)
    if field == 'params':
        fg.fig.subplots_adjust(bottom=0.11, top=0.95)
    if save:
        plt.savefig(savefig_path / filename, bbox_inches='tight')
    return fg


def plot_figure_response_predict_maps(path=work_chaim, species='H2O',
                                      field='response', bust='2010D-2011JFM',
                                      time_mean=None, time=None, 
                                      proj_key='PlateCarree', save=True):
    """response/predict maps (lat-lon) for cdas-plags, enso, ch4 for 2010D-2011JFM bust"""
    import xarray as xr
    import cartopy.crs as ccrs
    from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER
    from ML_OOP_stratosphere_gases import plot_like_results
    time_dict = {'2010D-2011JFM': ['2010-12', '2011-03'],
                 '2015OND': ['2015-10', '2015-12'],
                 '2016OND': ['2016-10', '2016-12']}
    col_dict = {'response': 'regressors', 'predict': 'opr'}
    if species == 'H2O':
        rds = xr.open_dataset(
            path /
            'MLR_H2O_latlon_cdas-plags_ch4_enso_2004-2019.nc')
        level = 82
        unit = 'ppmv'
    elif species == 't':
        rds = xr.open_dataset(
            path /
            'MLR_t_85hpa_latlon_cdas-plags_ch4_enso_1984-2019.nc')
        level = 85
        unit = 'K'
    elif species == 'u':
        rds = xr.open_dataset(
            path /
            'MLR_u_85hpa_latlon_cdas-plags_ch4_enso_1984-2019.nc')
        level = 85
        unit = r'm$\cdot$sec$^{-1}$'
    if time is None:
        time = time_dict.get(bust)
    fg = plot_like_results(rds, plot_key='{}_map'.format(field), level=level,
                           cartopy=True, time=time, time_mean=time_mean)
    rds = fg.data.sel(lat=slice(-60, 60))
    if time_mean == 'season':
        size = 4
    else:
        size = rds.time.size
    if size == 4:
        figsize = (15, 7)
        s_adjust = dict(
            top=0.955,
            bottom=0.115,
            left=0.03,
            right=0.97,
            hspace=0.08,
            wspace=0.15)
        rect = [0.1, 0.06, 0.8, 0.01]
        i_label = 9
    elif size == 3:
        figsize = (15, 5.5)   # bottom=0.2, top=0.9, left=0.05
        s_adjust = dict(top=0.945,
                        bottom=0.125,
                        left=0.04,
                        right=0.97,
                        hspace=0.03,
                        wspace=0.18)
        rect = [0.1, 0.06, 0.8, 0.015]
        i_label = 6
    proj = getattr(ccrs, proj_key)(central_longitude=0.0)
    if time_mean is not None:
        row = time_mean
    else:
        row = 'time'
    fg = rds.plot.contourf(col=col_dict.get(field), row=row,
                           add_colorbar=False,
                           cmap=predict_cmap, center=0.0, extend=None,
                           levels=41, subplot_kws={'projection': proj},
                           transform=ccrs.PlateCarree(), figsize=figsize)
    fg = add_horizontal_colorbar(
        fg, rect=rect, cbar_kwargs_dict={
            'label': unit})
    for i, ax in enumerate(fg.axes.flatten()):
        ax.coastlines(resolution='110m')
        if proj_key == 'PlateCarree':
            gl = ax.gridlines(crs=ccrs.PlateCarree(),
                              linewidth=1,
                              color='black',
                              alpha=0.5,
                              linestyle='--',
                              draw_labels=True)
            gl.xlabels_top = False
            gl.ylabels_right = False
            if i < i_label:
                gl.xlabels_bottom = False
            gl.xlabel_style = {'size': 9}
            gl.ylabel_style = {'size': 9}
            gl.xlines = True
            gl.ylines = True
            gl.xlocator = mticker.FixedLocator([-180, -120, -60, 0, 60, 120, 180])
            gl.ylocator = mticker.FixedLocator([-45, -30, -15, 0, 15, 30, 45])
            gl.xformatter = LONGITUDE_FORMATTER
            gl.yformatter = LATITUDE_FORMATTER
        else:
            gl = ax.gridlines(crs=ccrs.PlateCarree(),
                              linewidth=1,
                              color='black',
                              alpha=0.5,
                              linestyle='--',
                              draw_labels=False)
        if field == 'response':
            ax = remove_regressors_and_set_title(ax)
        elif field == 'predict':
            ax = remove_anomaly_and_set_title(ax, species=species)
        if time_mean != 'season':
            ax = remove_time_and_set_date(ax)
    fg.fig.tight_layout()
    fg.fig.subplots_adjust(**s_adjust)
    if time is not None and time_mean == 'season':
        bust = '{}_seasons'.format(time)
    filename = 'MLR_{}_{}_map_{}_cdas-plags_ch4_enso_{}.png'.format(species,
                                                                    field,
                                                                    level,
                                                                    bust)
    if save:
        fg.fig.savefig(savefig_path / filename, bbox_inches='tight', orientation='landscape')
    return fg


def plot_figure_14(path=work_chaim):
    fg = plot_figure_response_predict_maps(path, species='H2O',
                                           field='response',
                                           bust='2010D-2011JFM', save=True)
    print('Caption: ')
    print('The water vapor anomalies predictor response map for the 82.54 hPa level in the 2010-D to 2011-JFM forecast bust.')
    return fg


def plot_figure_15(path=work_chaim):
    fg = plot_figure_response_predict_maps(path, species='t', field='response',
                                           bust='2010D-2011JFM', save=True)
    print('Caption: ')
    print('The air temperature anomalies predictor response map for the 85 hPa level in the 2010-D to 2011-JFM forecast bust.')
    return fg


def plot_figure_16(path=work_chaim):
    fg = plot_figure_response_predict_maps(path, species='H2O',
                                           field='predict',
                                           bust='2010D-2011JFM', save=True)
    print('Caption: ')
    print('The water vapor anomalies, reconstruction and residuals maps for the 82.54 hPa level in the 2010-D to 2011-JFM forecast bust.')
    return fg


def plot_figure_17(path=work_chaim):
    fg = plot_figure_response_predict_maps(path, species='H2O',
                                           field='response',
                                           bust='2015OND', save=True)
    print('Caption: ')
    print('The water vapor anomalies predictor response map for the 82.54 hPa level in the 2015-OND forecast bust.')
    return fg


def plot_figure_18(path=work_chaim):
    fg = plot_figure_response_predict_maps(path, species='t', field='response',
                                           bust='2015OND', save=True)
    print('Caption: ')
    print('The air temperature anomalies predictor response map for the 85 hPa level in the 2015-OND forecast bust.')
    return fg


def plot_figure_19(path=work_chaim):
    fg = plot_figure_response_predict_maps(path, species='H2O',
                                           field='predict',
                                           bust='2015OND', save=True)
    print('Caption: ')
    print('The water vapor anomalies, reconstruction and residuals maps for the 82.54 hPa level in the 2015-OND forecast bust.')
    return fg


def plot_figure_20(path=work_chaim):
    fg = plot_figure_response_predict_maps(path, species='H2O',
                                           field='response',
                                           bust='2016OND', save=True)
    print('Caption: ')
    print('The water vapor anomalies predictor response map for the 82.54 hPa level in the 2016-OND forecast bust.')
    return fg


def plot_figure_21(path=work_chaim):
    fg = plot_figure_response_predict_maps(path, species='t', field='response',
                                           bust='2016OND', save=True)
    print('Caption: ')
    print('The air temperature anomalies predictor response map for the 85 hPa level in the 2016-OND forecast bust.')
    return fg


def plot_figure_22(path=work_chaim):
    fg = plot_figure_response_predict_maps(path, species='H2O',
                                           field='predict',
                                           bust='2016OND', save=True)
    print('Caption: ')
    print('The water vapor anomalies, reconstruction and residuals maps for the 82.54 hPa level in the 2016-OND forecast bust.')
    return fg


def plot_figure_23(path=work_chaim):
    fg = plot_figure_response_predict_maps(time=2009, species='H2O',
                                           field='response',
                                           time_mean='season', save=True)
    print('Caption: ')
    print('Seasonal water vapor anomalies predictor response maps for the 82.54 hPa level in 2009')
    return fg


def plot_figure_24(path=work_chaim):
    fg = plot_figure_response_predict_maps(time=2010, species='H2O',
                                           field='response',
                                           time_mean='season', save=True)
    print('Caption: ')
    print('Seasonal water vapor anomalies predictor response maps for the 82.54 hPa level in 2010')
    return fg


def plot_figure_25(path=work_chaim):
    fg = plot_figure_response_predict_maps(time=2009, species='t',
                                           field='response',
                                           time_mean='season', save=True)
    print('Caption: ')
    print('Seasonal air temperature anomalies predictor response maps for the 85 hPa level in 2009')
    return fg


def plot_figure_26(path=work_chaim):
    fg = plot_figure_response_predict_maps(time=2010, species='t',
                                           field='response',
                                           time_mean='season', save=True)
    print('Caption: ')
    print('Seasonal air temperature anomalies predictor response maps for the 85 hPa level in 2010')
    return fg


def plot_figure_27(path=work_chaim):
    fg = plot_figure_response_predict_maps(time=2009, species='u',
                                           field='response',
                                           time_mean='season', save=True)
    print('Caption: ')
    print('Seasonal zonal wind anomalies predictor response maps for the 85 hPa level in 2009')
    return fg


def plot_figure_28(path=work_chaim):
    fg = plot_figure_response_predict_maps(time=2010, species='u',
                                           field='response',
                                           time_mean='season', save=True)
    print('Caption: ')
    print('Seasonal zonal wind anomalies predictor response maps for the 85 hPa level in 2010')
    return fg


def plot_figure_poly2_lat(path=work_chaim):
    ncfile = 'MLR_H2O_latlon_cdas-plags_ch4_enso_poly_2_no_qbo^2_no_ch4_extra_2004-2019.nc'
    fg = plot_latlon_predict(ncfile, path=path, geo='lat', level=82.54,
                             bust_lines=True, save=True)


def plot_figure_poly2_lon(path=work_chaim):
    ncfile = 'MLR_H2O_latlon_cdas-plags_ch4_enso_poly_2_no_qbo^2_no_ch4_extra_2004-2019.nc'
    fg = plot_latlon_predict(ncfile, path=path, geo='lon', level=82.54,
                             bust_lines=True, save=True)
    
def plot_figure_poly2_params(path=work_chaim):
    ncfile = 'MLR_H2O_latlon_cdas-plags_ch4_enso_poly_2_no_qbo^2_no_ch4_extra_2004-2019.nc'
    fg = plot_feature_map(
        ncfile,
        path=path,
        feature='params',
        level=82,
        col_wrap=3,
        figsize=(
            15,
            5))
    plt.subplots_adjust(top=1.0,
                        bottom=0.101,
                        left=0.051,
                        right=0.955,
                        hspace=0.0,
                        wspace=0.21)
    return fg