#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
author: sbuchhorn
date: 28 Mar 2019
description: assign synthetic households to buildings in Lake County
"""

import pandas as pd
import random


# TEST DATA
hh = pd.read_csv("C:/Users/sbuchhorn/Desktop/2010pop/buildings/babydata/hh10149.csv")
bldg = pd.read_csv("C:/Users/sbuchhorn/Desktop/2010pop/buildings/babydata/bldg10149.csv")


def maz_filter(household, unmatched):
    # get pool of all the buildings in the same maz with res units != 0

    rowhh = hh[hh['household_id'] == household]
    hhmaz = rowhh.maz.values[0]
    bldgoptions = bldg[(bldg['subzone17'] == hhmaz) & (bldg['residential_units'] > 0)]

    if len(bldgoptions) == 0:
        print('no houses')
        unmatched.append(household)
        # have not built out unmatched pathway
    else:
        return bldgoptions



def maz_filter_remainder(unmatched):
    # not built out yet

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
    bldgoptions.loc[bldgoptions['classyear'] == hhyear + 1, 'choiceScore'] += 1
    bldgoptions.loc[bldgoptions['classyear'] == hhyear - 1, 'choiceScore'] += 1


    # score condo
    if hhcond > 0:
        bldgoptions.loc[bldgoptions['building_type_id'] == 1210, 'choiceScore'] += 1

    # single family attributes
    if hhtype in [1,2,3]:
        # business
        if hhbus == 1.0:
            bldgoptions.loc[bldgoptions['building_type_id'].isin([2130,2110,2120]), 'choiceScore'] += 1
        # bedrooms (estimated for one unit buildings only)
        if hhbroom >= 5:
            # the sqft estimation only goes up to 4, so let it get points for matching to 4
            hhbroom = 5
        bldgoptions.loc[(bldgoptions['residential_units'] == 1) &
                        (bldgoptions['bedroomsest'] == hhbroom), 'choiceScore'] += 2
        bldgoptions.loc[(bldgoptions['residential_units'] == 1) &
                        (bldgoptions['bedroomsest'] == hhbroom + 1), 'choiceScore'] += 1
        bldgoptions.loc[(bldgoptions['residential_units'] == 1) &
                        (bldgoptions['bedroomsest'] == hhbroom - 1), 'choiceScore'] += 1
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
    score = rankedPool.iloc[0]['choiceScore']

    return selectedID, score


def removeAndUpdate(buildingdf, hhdf, hhID, bldgID):
    # decrease the selected building's res_units count by one or remove building if 0
    hhdf[hhdf['household_id'] == hhID]['building_id'] = bldgID
    hhdf = hhdf[hhdf['household_id'] != hhID]

    try:
        units = buildingdf[buildingdf['TEMP_BLDG_ID'] == bldgID]['residential_units'].values[0]
    except IndexError:
        units = 0

    if units == 0:
        buildingdf = buildingdf[buildingdf['TEMP_BLDG_ID'] != bldgID]
    else:
        buildingdf.loc[buildingdf['TEMP_BLDG_ID'] == bldgID, 'residential_units'] = units - 1

    return buildingdf, hhdf


# setup
def setup(hh):
    hhids = [x for x in hh.household_id]
    #result df will be like household_id, pick order, building id, score
    resultdf = pd.DataFrame(index=hhids, columns=['pickorder','bldgid','score'])
    unmatched = []

    return resultdf, unmatched

# process flow
def choose_building(hhdf, bldgdf, resultdf, unmatched, pickorder=0):
    hhids = [x for x in hhdf.household_id]

    if len(hhids) > 0:
        chooserHH = random.choice(hhids)
        pickorder += 1

        # get options in maz
        bldgoptions = maz_filter(chooserHH, unmatched)
        # rate options
        ratedBldgOptions = rate_pool(chooserHH, bldgoptions)
        # select
        selectedID, score = assign_building(ratedBldgOptions)
        # assign and update
        bldg, hh = removeAndUpdate(bldgdf, hhdf, chooserHH,selectedID)

        resultdf.loc[chooserHH, ['pickorder','bldgid','score']] = [pickorder, selectedID, score]

        choose_building(hh, bldg, resultdf, pickorder)
    else:
        print('all done')

    return resultdf


resultdf, unmatched = setup(hh)
finalresult = choose_building(hh, bldg, resultdf, unmatched)

hhwid = hh.merge(finalresult,left_on='household_id',right_on=finalresult.index)
allinfo = hhwid.merge(bldg,right_on='TEMP_BLDG_ID',left_on='bldgid')
allinfo = allinfo[['household_id','maz','taz','puma',
         'BUS','CONP','BLD','classbldg','residential_units',
         'VALP','totalEstValue','land_value','improvement_value',
         'YBL','classyear','year_built',
         'RMSP','BDSP','bedroomsest','residential_sqft',
         'ACR','classacre','acres',
         'pickorder','bldgid','score']]