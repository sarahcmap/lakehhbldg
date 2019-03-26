#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""extra info
"""
import pandas as pd
import random

# buildingsfile
# get the csv from GIS (union of MAZ with buildings layer)
df = pd.read_csv("C:/Users/sbuchhorn/Desktop/2010pop/buildings/buildings_maz_lake.csv")
dfsorted = df.sort_values(['TEMP_BLDG_ID','Shape_Area'],ascending=[True,False])
df = dfsorted[~dfsorted.duplicated('TEMP_BLDG_ID',keep='first')]

# households
# keep in mind we'll probably have to go back and add in the extra attributes
hh = pd.read_csv("S:/AdminGroups/ResearchAnalysis/buchhorn/advanced_urban_models/populationsim/2010pop/urbansim/households.csv")

lakecountymaz = [i for i in range(8703,10599)]

lakehh = hh[hh.maz.isin(lakecountymaz)]


# TEST DATA
hh = pd.read_csv("C:/Users/sbuchhorn/Desktop/2010pop/buildings/babydata/hh10149.csv")
bldg = pd.read_csv("C:/Users/sbuchhorn/Desktop/2010pop/buildings/babydata/bldg10149.csv")

class building:
    # property: id 'TEMP_BLDG_ID'
    # property: maz 'subzone17'
    # property: taz 'zone17'
    'year_built'
    # year built 'classyear'
    # building type 'building_type_id'
    # res units 'residential_units'
    'totalEstValue'
    'classacre'
    'bedroomest'
    'classbldg'

class household:
    # property: id 'household_id'
    # property: maz 'maz'
    # property: taz 'taz'
    # pool of choices: output of function build pool
    # assigned building: output of function assign building
    # property value? 'VALP'
    # business? 'BUS'
    'ACR'
    'BDSP'
    'CONP'
    'YBL'

hhids = [x for x in hh.household_id]

# get random hh
chooserHH = random.choice(hhids)

bldgoptions = maz_filter(chooserHH)



def maz_filter(household):
    # get pool of all the buildings in the same maz with res units != 0

    rowhh = hh[hh['household_id'] == household]
    hhmaz = rowhh.maz.values[0]
    bldgoptions = bldg[(bldg['subzone17'] == hhmaz) & (bldg['residential_units'] > 0)]

    if len(bldgoptions) == 0:
        print('no houses')
    else:
        return bldgoptions

    # path 1b: add household to <LISTA>.  save for later.  after others are done, run through a filter location remainder function


def maz_filter_remainder(LISTA):
    # path 1b: get pool of all buildings in the same taz with res
#       units != 0 <and same building type>.  CANNOT CHANGE PUMAS (caveats).
    # for households that had no pool.  find nearby empty households after initial assignment and work through those.
        # HH CANNOT CHANGE PUMAS (well...given imperfect 00/10 geography match may we will relax this later).

    return location_pool



def rate_pool(household, location_pool):
    score_type()
    score_year()
    score_value()

    return rated_pool

def score_type(typea, typeideal):
def score_year():
def score_value():



def assign_building(rated_pool):
    # make a selection given the weights
    removeAndUpdate()

def removeAndUpdate():
    # decrease the selected building's res_units count by one or remove building if 0

    return updated buildings


