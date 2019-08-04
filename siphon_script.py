#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jul  4 13:55:37 2019

@author: ziskin
"""

from pathlib import Path
from strato_soundings import siphon_igra2_to_xarray
from strat_paths import work_chaim
# sound_path = Path('/home/ziskin/Work_Files/Chaim_Stratosphere_Data/sounding')
sound_path = work_chaim / 'sounding'
cwd = Path().cwd()
import pandas as pd
skipped = 0
already_dl = 0
stations = pd.read_csv(cwd/ 'igra_eq_stations.txt', index_col=0)
for station in stations.values:
    st = station[0]
    ds = siphon_igra2_to_xarray(st, path=sound_path)
    if ds == '1':
        already_dl += 1
    elif ds == '2':
        skipped += 1
    print('already dl: {}, skipped so far: {}'.format(already_dl, skipped))
print('ALL FILES DONE!')
