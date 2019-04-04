#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""extra info
"""
import pandas as pd
bldgs = pd.read_csv("C:/Users/sbuchhorn/Desktop/2010pop/buildings/lakebuildingsextraatts_2.csv")
hh = pd.read_csv("C:/Users/sbuchhorn/Desktop/2010pop/buildings/current/lakehhextraatts.csv")

maz_selections = [10254, 10259]
taz_selections = [2327, 2350, 2353]
puma = 3303

bldgstest2 = bldgs[bldgs['subzone17'].isin(maz_selections)]
hhtest2 = hh[hh['maz'].isin(maz_selections)]

bldgstest2 = bldgs[bldgs['zone17'].isin(taz_selections)]
hhtest2 = hh[hh['taz'].isin(taz_selections)]

bldgstest2 = bldgs[bldgs['puma5'] == puma]
hhtest2 = hh[hh['puma'] == puma]

bldgstest2.to_csv("C:/Users/sbuchhorn/Desktop/2010pop/buildings/babydata/bldg6.csv",index=False)
hhtest2.to_csv("C:/Users/sbuchhorn/Desktop/2010pop/buildings/babydata/hh6.csv", index=False)