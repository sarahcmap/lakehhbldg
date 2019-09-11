#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
author: sbuchhorn
date: 28 Mar 2019
updated: 11 Sept 2019
description: assign synthetic households to buildings in Lake County
"""

import pandas as pd
import random
import numpy as np
import time
import sys
import os

# end with slash!
outputdir = "T:/buchhorn/buildingtesting/test3/"

# check that output dirs are ok
if not os.path.exists(outputdir):
    sys.stderr.write("output folder doesn't exist! \n fix before continuing")

# TEST DATA
fullhh = pd.read_csv("T:/buchhorn/buildingtesting/hhtest3.csv")
fullhh = fullhh[fullhh['BLD'] != 10]    # exclude households not in buildings (boat, rv, van, etc)
fullbldg = pd.read_csv("T:/buchhorn/buildingtesting/bldgtest3.csv")
fullbldg['remaining_residential_units'] = fullbldg['residential_units']

neartaz = pd.read_csv("T:/buchhorn/buildingtesting/sz17neighbor.csv")
neighborDict = neartaz.groupby('zone17')['nbr_zone17'].apply(list).to_dict()

puma = set([x for x in fullhh['puma']])
random.shuffle(puma)


def maz_filter(household, unmatched):
    # get pool of all the buildings in the same maz with res units != 0

    rowhh = hh[hh['household_id'] == household]
    hhmaz = rowhh.maz.values[0]
    bldgoptions = bldg[(bldg['subzone17'] == hhmaz) & (bldg['remaining_residential_units'] > 0)].copy()

    if len(bldgoptions) == 0:
        unmatched.append(household)
        return bldgoptions, unmatched

    else:
        return bldgoptions, unmatched



def tazFilter(household):
    rowhh = hh[hh['household_id'] == household]
    hhtaz = rowhh.taz.values[0]
    bldgoptions = bldg[(bldg['zone17'] == hhtaz) & (bldg['remaining_residential_units'] > 0)].copy()

    if len(bldgoptions) == 0:
        return bldgoptions

    else:
        return bldgoptions



def tazNeighborFilter(household):
    rowhh = hh[hh['household_id'] == household]
    hhtaz = rowhh.taz.values[0]
    bldgoptions = bldg[(bldg['zone17'].isin(neighborDict[hhtaz])) & (bldg['remaining_residential_units'] > 0)].copy()

    if len(bldgoptions) == 0:
        return bldgoptions

    else:
        return bldgoptions


def pumaFilter(household):
    rowhh = hh[hh['household_id'] == household]
    # don't need puma filter anymore since we're splitting out by puma now
    bldgoptions = bldg[bldg['remaining_residential_units'] > 0].copy()

    if len(bldgoptions) == 0:
        sys.stderr.write('no puma houses')
        return bldgoptions

    else:
        return bldgoptions



def rate_pool(household, bldgoptions):
    bldgoptions['choiceScore'] = 0

    rowhh = hh.loc[hh['household_id'] == household]

    # determine top quartile once based only on type
    hhtype = rowhh.BLD.values[0]
    scorecol = 'score{}'.format(hhtype.astype(int))
    bldgoptions['choiceScore'] = bldgoptions[scorecol]

    bldgoptions = bldgoptions.sort_values('choiceScore',ascending=False)
    # get list of unique scores and get top quartile cutoff
    topquartile = np.percentile(bldgoptions.choiceScore.unique(), 75)
    # take only rows from df where score is greater or equal to this cutoff
    bldgoptions = bldgoptions[bldgoptions['choiceScore'] >= topquartile]
    # max 100 options
    if len(bldgoptions) > 100:
        bldgoptions = bldgoptions.sample(100)

    # add detail as appropriate
    hhcond = rowhh.CONP.values[0]
    # score condo
    if hhcond > 0:
        bldgoptions.loc[bldgoptions['condo'] == 1, 'choiceScore'] += 1  # condo, hotel, or office building

    hhbus = rowhh.BUS.values[0]
    hhacre = rowhh.ACR.values[0]
    hhbroom = rowhh.BDSP2.values[0]
    hhvalp = rowhh.VALP.values[0]
    hhyear = rowhh.YBL2.values[0]

    # score year
    yscorecol = 'yscore{}'.format(hhyear.astype(int))
    bldgoptions.loc[:,'choiceScore'] += bldgoptions[yscorecol]

    # single family attributes
    if hhtype in [1,2,3]:
        # business
        if hhbus == 1.0:
            bldgoptions.loc[bldgoptions['building_type_id'].isin([2130, 2110, 2120]), 'choiceScore'] += 1
        # lot size
        bldgoptions.loc[bldgoptions['classacre'] == hhacre, 'choiceScore'] += 1

        # bedrooms (estimated for one unit buildings only, undefined otherwise so don't need that filter)
        bldgoptions.loc[bldgoptions['bedroomsest'] == hhbroom, 'choiceScore'] += 2
        bldgoptions.loc[bldgoptions['bedroomsest'] == hhbroom + 1, 'choiceScore'] += 1
        bldgoptions.loc[bldgoptions['bedroomsest'] == hhbroom - 1, 'choiceScore'] += 1

        # Value
        # +/- 20%
        bldgoptions.loc[(hhvalp - bldgoptions['twentyval'] < bldgoptions['totalEstValue']) &
                        (bldgoptions['totalEstValue'] < hhvalp + bldgoptions['twentyval']), 'choiceScore'] += 2
        # from 20-40% lower
        bldgoptions.loc[(hhvalp - bldgoptions['fortyval'] < bldgoptions['totalEstValue']) &
                        (bldgoptions['totalEstValue'] < hhvalp - bldgoptions['twentyval']), 'choiceScore'] += 1
        # from 20-40% higher
        bldgoptions.loc[(hhvalp + bldgoptions['twentyval'] < bldgoptions['totalEstValue']) &
                        (bldgoptions['totalEstValue'] < hhvalp + bldgoptions['fortyval']), 'choiceScore'] += 1

    return bldgoptions



def assign_building(rated_pool):
    # sort values by score
    rankedPool = rated_pool.sort_values('choiceScore',ascending=False).reset_index()
    topscore = rankedPool.iloc[0]['choiceScore']  # for QA/QC
    # get list of scores for weights
    toplist = [x for x in rankedPool['choiceScore']]
    # choose random weighted by the score, unless the only choice is zero
    try:
        selectedID = rankedPool.sample(1, weights=toplist).iloc[0]['building_id']
    except ValueError:
        selectedID = rankedPool.sample(1).iloc[0]['building_id']

    score = rankedPool[rankedPool['building_id'] == selectedID]['choiceScore'].values[0]

    return selectedID, score, topscore


def removeAndUpdate(buildingdf, hhdf, hhID, bldgID):
    # decrease the selected building's res_units count by one or remove building if 0
    hhdf.loc[hhdf['household_id'] == hhID, 'building_id'] = bldgID
    hhdf = hhdf.loc[hhdf['household_id'] != hhID].copy()

    try:
        units = buildingdf[buildingdf['building_id'] == bldgID]['remaining_residential_units'].values[0]
    except IndexError:
        units = 0

    if units == 0:
        buildingdf = buildingdf.loc[buildingdf['building_id'] != bldgID].copy()
    else:
        buildingdf.loc[buildingdf['building_id'] == bldgID, 'remaining_residential_units'] = units - 1

    return buildingdf, hhdf


# setup
def setup(hh):
    hhids = [x for x in hh.household_id]
    #result df will be like household_id, pick order, building id, score
    resultdf = pd.DataFrame(index=hhids, columns=['pickorder','bldgid','score','topscore'])
    unmatched = []
    failed = []
    # randomize once in beginning
    random.shuffle(hhids)

    return resultdf, unmatched, failed, hhids


def matchHouseholds(hhids, unmatched, bldg, hhdf):
    start = time.time()
    pickorder = 0

    for i in hhids:
        pickorder += 1

        if pickorder % 10000 == 0:
            sys.stdout.write('working on hh {}'.format(pickorder))

        # get options in maz
        bldgoptions, unmatched = maz_filter(i, unmatched)

        if len(bldgoptions) > 0:
            # rate options
            ratedBldgOptions = rate_pool(i, bldgoptions)
            # select
            selectedID, score, topscore = assign_building(ratedBldgOptions)
            # assign and update
            bldg, hhdf = removeAndUpdate(bldg, hhdf, i, selectedID)

            resultdf.loc[i, ['pickorder','bldgid','score','topscore']] = [pickorder, selectedID, score, topscore]

    end = time.time()
    sys.stdout.write('\n maz level done. Took {} seconds'.format(end-start))

    return resultdf, unmatched, pickorder


def matchRemainder(unmatched, resultdf, pickorder, bldg, hhdf):
    start = time.time()

    for i in unmatched:
        pickorder += 1

        # get options in taz
        bldgoptions = tazFilter(i)

        if len(bldgoptions) > 0:
            # rate options
            ratedBldgOptions = rate_pool(i, bldgoptions)
            # select
            selectedID, score, topscore = assign_building(ratedBldgOptions)
            # assign and update
            bldg, hhdf = removeAndUpdate(bldg, hhdf, i, selectedID)

            resultdf.loc[i, ['pickorder', 'bldgid', 'score', 'topscore']] = [pickorder, selectedID, score, topscore]

        else:
            bldgoptions = tazNeighborFilter(i)

            if len(bldgoptions) > 0:
                # rate options
                ratedBldgOptions = rate_pool(i, bldgoptions)
                # select
                selectedID, score, topscore = assign_building(ratedBldgOptions)
                # assign and update
                bldg, hhdf = removeAndUpdate(bldg, hhdf, i, selectedID)

                resultdf.loc[i, ['pickorder', 'bldgid', 'score','topscore']] = [pickorder, selectedID, score, topscore]

            else:
                bldgoptions = pumaFilter(i)

                if len(bldgoptions) > 0:
                    # rate options
                    ratedBldgOptions = rate_pool(i, bldgoptions)
                    # select
                    selectedID, score, topscore = assign_building(ratedBldgOptions)
                    # assign and update
                    bldg, hhdf = removeAndUpdate(bldg, hhdf, i, selectedID)

                    resultdf.loc[i, ['pickorder', 'bldgid', 'score', 'topscore']] = [pickorder, selectedID, score, topscore]

                else:
                    sys.stderr.write('hh cannot be matched')
                    failed.append(i)

    end = time.time()
    sys.stdout.write('\n Remainder matching done. Took {} seconds'.format(end-start))

    return resultdf, failed


#flow
for i in puma:
    print("working on puma {}".format(i))
    hh = fullhh[fullhh['puma'] == i]
    bldg = fullbldg[fullbldg['puma5'] == i]

    resultdf, unmatched, failed, hhids = setup(hh)
    mazresult, unmatched, pickorder = matchHouseholds(hhids=hhids, unmatched=unmatched, bldg=bldg, hhdf=hh.copy())
    finalresult, failed = matchRemainder(unmatched=unmatched, resultdf=mazresult, pickorder=pickorder, bldg=bldg, hhdf=hh)

    hh.to_csv(outputdir + "hh_{}.csv".format(i))
    finalresult.to_csv(outputdir + "finalresult_{}.csv".format(i))
    bldg.to_csv(outputdir + "bldg_{}.csv".format(i))
    seriesfailed = pd.Series(failed)
    seriesfailed.to_csv(outputdir + "kanefailed_{}.csv".format(i))



    #
    # hhwid = hh.merge(finalresult,left_on='household_id',right_on=finalresult.index)
    # allinfo = hhwid.merge(bldg, right_on='building_id', left_on='bldgid')
    # allinfo = allinfo[['household_id','maz','subzone17','taz','zone17','puma',
    #          'BUS','CONP','BLD','classbldg', 'building_type_id', 'remaining_residential_units','residential_units',
    #          'VALP','totalEstValue','improvement_value',
    #          'YBL2','classyear','year_built', #land_value
    #          'RMSP','BDSP2','bedroomsest','residential_sqft',
    #          'ACR','classacre','acres',
    #          'pickorder','bldgid','score','topscore']]
    #
    # allinfo.to_csv(outputdir + "r_{}.csv".format(i), index=False)
    # dfnotmatched = allinfo[allinfo['BLD'] != allinfo['classbldg']]
    # a = dfnotmatched.groupby(['subzone17','BLD']).classbldg.value_counts().rename('count').reset_index()
    # a.to_csv(outputdir + "mismatch_{}.csv".format(i), header=['maz','originaltype','newtype','count'], index=False)
    # seriesfailed = pd.Series(failed)
    # seriesfailed.to_csv(outputdir + "failed_{}.csv".format(i))
