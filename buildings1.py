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


class Household:
    def __init__(self, ID, p, bID, score):
        self.hhID = ID
        self.pickOrder = p
        self.buildingID = bID
        self.score = score


hhids = [x for x in hh.household_id]


#result dictionary will be like household_id : [pick order, building id, score]
# get random hh
chooserHH = random.choice(hhids)
# get options in maz
bldgoptions = maz_filter(chooserHH)
# rate options
ratedBldgOptions = rate_pool(chooserHH, bldgoptions)
# select
selectedID = assign_building(ratedBldgOptions)
# assign and update
removeAndUpdate(bldg, hh, chooserHH,selectedID)


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



def rate_pool(household, bldgoptions):
    bldgoptions['choiceScore'] = 0

    rowhh = hh[hh['household_id'] == household]

    hhtype = rowhh.BLD.values[0]
    hhyear = rowhh.YBL.values[0]
    hhbus = rowhh.BUS.values[0]
    hhbroom = rowhh.BDSP.values[0]
    hhvalp = rowhh.VALP.values[0]
    hhcond = rowhh.CONP.values[0]
    hhacre = rowhh.ACR.values[0]

    # score type
    bldgoptions.loc[bldgoptions['classbldg'] == hhtype, 'choiceScore'] += 5

    # score year
    bldgoptions.loc[bldgoptions['classyear'] == hhyear, 'choiceScore'] += 2
    bldgoptions.loc[bldgoptions['classyear'] == hhyear +- 1, 'choiceScore'] += 1

    # score condo
    if hhcond > 0:
        bldgoptions.loc[bldgoptions['building_type_id'] == 1210, 'choiceScore'] += 1

    # single family attributes
    if hhtype in [1,2,3]:
        # business
        if hhbus == 1.0:
            bldgoptions.loc[bldgoptions['building_type_id'].isin([2130,2110,2120]), 'choiceScore'] += 2
        # bedrooms (estimated for one unit buildings only)
        bldgoptions.loc[(bldgoptions['residential_units'] == 1) &
                        (bldgoptions['bedroomsest'] == hhbroom), 'choiceScore'] += 2
        bldgoptions.loc[(bldgoptions['residential_units'] == 1) &
                        (bldgoptions['bedroomsest'] == hhbroom +- 1), 'choiceScore'] += 1
        # lot size
        bldgoptions.loc[bldgoptions['classacre'] == hhacre, 'choiceScore'] += 2
        # value (for one unit buildings only)
        bldgoptions.loc[(bldgoptions['residential_units'] == 1) &
                        (hhvalp - 5000 < bldgoptions['totalEstValue']) &
                        (bldgoptions['totalEstValue'] < hhvalp + 5000), 'choiceScore'] += 2


    return bldgoptions



def assign_building(rated_pool):
    # make a selection given the weights
    rankedPool = rated_pool.sort_values('choiceScore',ascending=False).reset_index()
    # for initial testing, give them top choice
    selectedID = rankedPool.iloc[0]['TEMP_BLDG_ID']

    return selectedID


def removeAndUpdate(buildingdf, hhdf, hhID, bldgID):
    # decrease the selected building's res_units count by one or remove building if 0
    hhdf[hhdf['household_id'] == hhID]['building_id'] = bldgID
    hhdf = hhdf[~hhdf['household_id'] == hhID]
    units = buildingdf[buildingdf['TEMP_BLDG_ID'] == bldgID]['residential_units'].values[0]
    if units == 1:
        buildingdf = buildingdf[~buildingdf['TEMP_BLDG_ID'] == bldgID]
    else:
        buildingdf.loc[buildingdf['TEMP_BLDG_ID'] == bldgID, 'residential_units'] = units - 1

    return buildingdf, hhdf

    return updated buildings


