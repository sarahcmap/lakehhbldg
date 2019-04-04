#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
author: sbuchhorn
date: 28 Mar 2019
description: assign synthetic households to buildings in Lake County
"""

import pandas as pd
import random
import numpy as np


# TEST DATA
hh = pd.read_csv("C:/Users/sbuchhorn/Desktop/2010pop/buildings/babydata/hh6.csv")
bldg = pd.read_csv("C:/Users/sbuchhorn/Desktop/2010pop/buildings/babydata/bldg6.csv")
neartaz = pd.read_csv("C:/Users/sbuchhorn/Desktop/2010pop/buildings/lakeneartaztable.csv")
neighborDict = neartaz.groupby('zone17')['nbr_zone17'].apply(list).to_dict()


def maz_filter(household, unmatched):
    # get pool of all the buildings in the same maz with res units != 0

    rowhh = hh[hh['household_id'] == household]
    hhmaz = rowhh.maz.values[0]
    bldgoptions = bldg[(bldg['subzone17'] == hhmaz) & (bldg['residential_units'] > 0)].copy()

    if len(bldgoptions) == 0:
        print('no houses')
        unmatched.append(household)
        return bldgoptions, unmatched

        # have not built out unmatched pathway
    else:
        return bldgoptions, unmatched



def tazFilter(household):
    rowhh = hh[hh['household_id'] == household]
    hhtaz = rowhh.taz.values[0]
    bldgoptions = bldg[(bldg['zone17'] == hhtaz) & (bldg['residential_units'] > 0)].copy()

    if len(bldgoptions) == 0:
        print('no taz houses')
        return bldgoptions

    else:
        return bldgoptions



def tazNeighborFilter(household):
    rowhh = hh[hh['household_id'] == household]
    hhtaz = rowhh.taz.values[0]
    bldgoptions = bldg[(bldg['zone17'].isin(neighborDict[hhtaz])) & (bldg['residential_units'] > 0)].copy()

    if len(bldgoptions) == 0:
        print('no taz houses')
        return bldgoptions

    else:
        return bldgoptions


def pumaFilter(household):
    rowhh = hh[hh['household_id'] == household]
    hhpuma = rowhh.puma.values[0]
    bldgoptions = bldg[(bldg['puma5'] == hhpuma) & (bldg['residential_units'] > 0)].copy()

    if len(bldgoptions) == 0:
        print('no puma houses')
        return bldgoptions

    else:
        return bldgoptions



def rate_pool(household, bldgoptions):
    bldgoptions['choiceScore'] = 0

    rowhh = hh.loc[hh['household_id'] == household]

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
        bldgoptions['tenval'] = bldgoptions['totalEstValue'] * 0.1
        bldgoptions['twentyfiveval'] = bldgoptions['totalEstValue'] * 0.25
        # +/- 10%
        bldgoptions.loc[(bldgoptions['residential_units'] == 1) &
                        (hhvalp - bldgoptions['tenval'] < bldgoptions['totalEstValue']) &
                        (bldgoptions['totalEstValue'] < hhvalp + bldgoptions['tenval']), 'choiceScore'] += 2
        # from 10-25% lower
        bldgoptions.loc[(bldgoptions['residential_units'] == 1) &
                        (hhvalp - bldgoptions['twentyfiveval'] < bldgoptions['totalEstValue']) &
                        (bldgoptions['totalEstValue'] < hhvalp - bldgoptions['tenval']), 'choiceScore'] += 1
        # from 10-25% higher
        bldgoptions.loc[(bldgoptions['residential_units'] == 1) &
                        (hhvalp + bldgoptions['tenval'] < bldgoptions['totalEstValue']) &
                        (bldgoptions['totalEstValue'] < hhvalp + bldgoptions['twentyfiveval']), 'choiceScore'] += 1


    return bldgoptions



def assign_building(rated_pool):
    # make a selection given the weights
    rankedPool = rated_pool.sort_values('choiceScore',ascending=False).reset_index()
    # give them random from top...quartile of unique values
    topquartile = np.percentile(rankedPool.choiceScore.unique(), 75)
    if topquartile >=2:
        rankedPoolTop = rankedPool[rankedPool['choiceScore'] >= topquartile]
        selectedID = rankedPoolTop.sample(1).iloc[0]['building_id']
    else: # if very low, just get the top one
        topscore = rankedPool.iloc[0]
        selectedID = topscore['building_id']
    score = rankedPool[rankedPool['building_id'] == selectedID]['choiceScore'].values[0]

    return selectedID, score


def removeAndUpdate(buildingdf, hhdf, hhID, bldgID):
    # decrease the selected building's res_units count by one or remove building if 0
    hhdf.loc[hhdf['household_id'] == hhID, 'building_id'] = bldgID
    hhdf = hhdf.loc[hhdf['household_id'] != hhID].copy()

    try:
        units = buildingdf[buildingdf['building_id'] == bldgID]['residential_units'].values[0]
    except IndexError:
        units = 0

    if units == 0:
        buildingdf = buildingdf.loc[buildingdf['building_id'] != bldgID].copy()
    else:
        buildingdf.loc[buildingdf['building_id'] == bldgID, 'residential_units'] = units - 1

    return buildingdf, hhdf


# setup
def setup(hh):
    hhids = [x for x in hh.household_id]
    #result df will be like household_id, pick order, building id, score
    resultdf = pd.DataFrame(index=hhids, columns=['pickorder','bldgid','score'])
    unmatched = []
    failed = []
    # randomize once in beginning
    random.shuffle(hhids)

    return resultdf, unmatched, failed, hhids


def matchHouseholds(hhids, unmatched, bldg, hhdf):
    pickorder = 0

    for i in hhids:
        pickorder += 1

        # get options in maz
        bldgoptions, unmatched = maz_filter(i, unmatched)

        if len(bldgoptions) > 0:
            # rate options
            ratedBldgOptions = rate_pool(i, bldgoptions)
            # select
            selectedID, score = assign_building(ratedBldgOptions)
            # assign and update
            bldg, hhdf = removeAndUpdate(bldg, hhdf, i, selectedID)

            resultdf.loc[i, ['pickorder','bldgid','score']] = [pickorder, selectedID, score]

        else:
            # is this necessary/doing anything?
            hhdf = hhdf.loc[hhdf['household_id'] != i].copy()

    print('maz level done at {}'.format(pickorder))

    return resultdf, unmatched, pickorder


def matchRemainder(unmatched, resultdf, pickorder, bldg, hhdf):

    for i in unmatched:
        pickorder += 1

        # get options in taz
        bldgoptions = tazFilter(i)

        if len(bldgoptions) > 0:
            # rate options
            ratedBldgOptions = rate_pool(i, bldgoptions)
            # select
            selectedID, score = assign_building(ratedBldgOptions)
            # assign and update
            bldg, hhdf = removeAndUpdate(bldg, hhdf, i, selectedID)

            resultdf.loc[i, ['pickorder', 'bldgid', 'score']] = [pickorder, selectedID, score]

        else:
            bldgoptions = tazNeighborFilter(i)
            print('step2')

            if len(bldgoptions) > 0:
                # rate options
                ratedBldgOptions = rate_pool(i, bldgoptions)
                # select
                selectedID, score = assign_building(ratedBldgOptions)
                # assign and update
                bldg, hhdf = removeAndUpdate(bldg, hhdf, i, selectedID)

                resultdf.loc[i, ['pickorder', 'bldgid', 'score']] = [pickorder, selectedID, score]

            else:
                bldgoptions = pumaFilter(i)
                print('step3')

                if len(bldgoptions) > 0:
                    # rate options
                    ratedBldgOptions = rate_pool(i, bldgoptions)
                    # select
                    selectedID, score = assign_building(ratedBldgOptions)
                    # assign and update
                    bldg, hhdf = removeAndUpdate(bldg, hhdf, i, selectedID)

                    resultdf.loc[i, ['pickorder', 'bldgid', 'score']] = [pickorder, selectedID, score]

                else:
                    print('hh cannot be matched')
                    failed.append(i)

    print('all done')

    return resultdf, failed



resultdf, unmatched, failed, hhids = setup(hh)
mazresult, unmatched, pickorder = matchHouseholds(hhids=hhids, unmatched=unmatched, bldg=bldg, hhdf=hh.copy())
finalresult, failed = matchRemainder(unmatched=unmatched, resultdf=mazresult, pickorder=pickorder, bldg=bldg, hhdf=hh)


hhwid = hh.merge(finalresult,left_on='household_id',right_on=finalresult.index)
allinfo = hhwid.merge(bldg, right_on='building_id', left_on='bldgid')
allinfo = allinfo[['household_id','maz','subzone17','taz','zone17','puma',
         'BUS','CONP','BLD','classbldg', 'building_type_id', 'residential_units',
         'VALP','totalEstValue','land_value','improvement_value',
         'YBL','classyear','year_built',
         'RMSP','BDSP','bedroomsest','residential_sqft',
         'ACR','classacre','acres',
         'pickorder','bldgid','score']]