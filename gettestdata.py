#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""extra info
"""
import pandas as pd
bldgs = pd.read_csv("C:/Users/sbuchhorn/Desktop/2010pop/buildings/lakebuildingsextraatts_2.csv")
hh = pd.read_csv("C:/Users/sbuchhorn/Desktop/2010pop/buildings/current/lakehhextraatts.csv")

maz_selections = [10254, 10259]
taz_selections = [2326, 2327, 2350, 2351, 2328, 2329, 2353, 2354, 2355, 2352]

bldgstest2 = bldgs[bldgs['subzone17'].isin(maz_selections)]
hhtest2 = hh[hh['maz'].isin(maz_selections)]

bldgstest2 = bldgs[bldgs['zone17'].isin(taz_selections)]
hhtest2 = hh[hh['taz'].isin(taz_selections)]

bldgstest2.to_csv("C:/Users/sbuchhorn/Desktop/2010pop/buildings/babydata/bldg4.csv",index=False)
hhtest2.to_csv("C:/Users/sbuchhorn/Desktop/2010pop/buildings/babydata/hh4.csv", index=False)