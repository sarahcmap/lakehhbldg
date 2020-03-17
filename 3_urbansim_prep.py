"""
Author: sbuchhorn
Last Update: 9 April 2019

This file prepares the output of the 1_fix_income process (with household ids and serialno column from 2_hh_nums) for
urbansim and travel modeling.  or, it takes the direct output from the popsim run

The same thing (direct from popsim version) is in 3_urbansim_prep.ipynb

"""
import pandas as pd

finaldf = pd.read_csv("H:/2010pop/popsim7/post/finaldf_serial_real_full.csv")
# if using results from popsim directly:
hh = pd.read_csv("S:/AdminGroups/ResearchAnalysis/buchhorn/advanced_urban_models/populationsim/"
                 "2010pop/popsim19/output/synthetic_households.csv")
people = pd.read_csv("S:/AdminGroups/ResearchAnalysis/buchhorn/advanced_urban_models/"
                 "populationsim/2010pop/popsim19/output/synthetic_persons.csv")
finaldf = hh.merge(people,how='left',on='household_id')


# HOUSEHOLDS FOR URBANSIM
finaldf.loc[finaldf['AGEP'] < 18, 'childflag'] = 1  # switched to 16 - switch back to 18 for urbansim
finaldf.loc[finaldf['ESR'].isin([1,2,4,5]), 'workerflag'] = 1
finaldf.loc[finaldf['MV'].isin([1,2,3]), 'recent_mover'] = 1
finaldf.loc[finaldf['MV'].isin([4,5,6,7]), 'recent_mover'] = 0
finaldf.loc[finaldf['TEN'].isin([1,2]), 'tenure'] = 1
finaldf.loc[finaldf['TEN'].isin([3,4]), 'tenure'] = 2

#a = finaldf.groupby('newnewid').agg({'childflag':'sum','workerflag':'sum'})
a = finaldf.groupby('household_id').agg({'childflag':'sum','workerflag':'sum'})

# for the household file, we just keep the entry for householder
finalhh = finaldf[finaldf['RELP'] == 0]
#finalhh = finalhh.merge(a, how='left',on='newnewid')
finalhh = finalhh.merge(a, how='left',on='household_id')

# list of columns to keep
household_list = [
    'newnewid',
    'HINCP12',
    'HINCP10',
    'TEN',
    'tenure',
    'VEH',
    'RAC1P',
    'AGEP',
    'childflag_y',
    'workerflag_y',
    'serialno',
    'NP',
    'MV',
    'HHT',
    'TYPE',
    'NOC',
    'BLD',
    'maz',
    'TAZ',
    'recent_mover',
    'PUMA'
]
# version for direct from popsim
household_list = [
    'household_id',
    'HINCP12',
    'TEN',
   'tenure',
    'VEH',
    'RAC1P',
    'AGEP',
    'childflag_y',
    'workerflag_y',
    'SERIALNO_RIGHT',
    'YEAR',
    'NP',
    'MV',
    'HHT',
    'TYPE',
    'NOC',
    'BLD',
    'MAZ_x',
    'TAZ_x',
   'recent_mover',
    'PUMA_x',
    'BUS',
    'VALP',
    'YBL',
    'CONP',
    'RMSP',
    'BDSP',
    'ACR'
]

household = finalhh[household_list]

household.to_csv("D:/2010lakecountypop/popsim18/post/hh.csv",index=False)

# PERSONS FOR URBANSIM

# add person_id
#finaldf.sort_values(['newnewid'], inplace=True)
finaldf.sort_values(['household_id'], inplace=True)
finaldf.reset_index(inplace=True)
finaldf['person_id'] = finaldf.index + 1

# member id
finaldf.loc[~finaldf['per_num'].isnull(),'member_id'] = finaldf['per_num']
finaldf.loc[~finaldf['SPORDER'].isnull(),'member_id'] = finaldf['SPORDER']
# for direct
finaldf['member_id'] = finaldf['per_num']

# 2012 person income
finaldf.loc[~finaldf['ADJINC_x'].isnull(),'income12'] = (finaldf['ADJINC_x'] / 1000000) * finaldf['PERNP']
finaldf.loc[~finaldf['ADJINC'].isnull(),'income12'] = (finaldf['ADJINC'] / 1000000) * finaldf['PERNP']
# direct
finaldf['income12'] = (finaldf['ADJINC'] / 1000000) * finaldf['PERNP']

# person attributes.  run one at a time!
finaldf.loc[finaldf['SCH'].isin([2,3]),'student_status'] = 1
finaldf.loc[finaldf['ESR'].isin([1,2,4,5]),'worker_status'] = 1
finaldf.loc[finaldf['JWTR'] == 11,'work_at_home'] = 1

# list of columns to keep
person_list = [
    'newnewid',
    'member_id',
    'AGEP',
    'SCHL',
    'RAC1P',
    'RELP',
    'SEX',
    'SCH',
    'ESR',
    'WKHP',
    'JWTR',
    'income12',
    'person_id',
    'student_status',
    'worker_status',
    'work_at_home',
    'SCHG',
    'WKW',
    'HISP',
    'MSP',
    'POVPIP',
    'INDP'
]

person_list = [
    'household_id',
    'member_id',
    'AGEP',
    'SCHL',
    'RAC1P',
    'RELP',
    'SEX',
    'SCH',
    'ESR',
    'WKHP',
    'JWTR',
    'income12',
    'person_id',
    'student_status',
    'worker_status',
    'work_at_home',
    'SCHG',
    'WKW',
    'HISP',
    'MSP',
    'POVPIP',
    'INDP'
]


person = finaldf[person_list]

person.to_csv("D:/2010lakecountypop/popsim18/post/people.csv",index=False)



