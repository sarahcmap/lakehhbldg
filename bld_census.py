#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Get BLD data from 2008-2012 ACS, or our own building file

When developing based on buildings file, note the assumption that households are
distributed as the household building types are distributed
"""
from census import Census
import pandas as pd


YEAR = 2012  # Final year of 5-year ACS dataset (e.g. 2012 for 2008-2012 data)

# didn't use this, but here are tracts in region
TRACTS_21CO_FC  = "C:\\Users\\sbuchhorn\\Desktop\\populationsim\\popsimpython\\tracts.csv"
tractsdf = pd.read_csv(TRACTS_21CO_FC)
tracts17 = [i for i in tractsdf[tractsdf['STATEFP10'] == 17]['GEOID10'].astype(str)]
tracts171 = [x[-6:] for x in tracts17]
tracts_21co = list(set(tractsdf['GEOID10']))

# get a census API key
c = Census("966634657b884eed55d60321c0ad25f828b66bae", year=YEAR)
#https://api.census.gov/data/2012/acs/acs5/variables.json

for state_fips in ('17', '18', '55'):
    # UNITS IN STRUCTURE
    unitslist = c.acs5.get(['B25024_001E',#total
                            'B25024_002E', #1, detached
                           'B25024_003E', #1, attached
                           'B25024_004E', # 2
                           'B25024_005E', # 3 or 4
                           'B25024_006E', # 5 to 9
                           'B25024_007E', # 10 to 19
                           'B25024_008E', # 20 to 49
                           'B25024_009E', # 50+
                           'B25024_010E', # mobile home
                           'B25024_011E'], # boat, rv, van, etc.
                           geo={'for': 'tract:*', 'in': 'state:{}'.format(state_fips)})
    df = pd.DataFrame(unitslist)
    df.to_csv('/Users/sarahbuchhorn/Desktop/cmap_wfh/urbansim/acs_bld_data/df{}_units.csv'.format(state_fips))

# now get pct for each category (just swapping out state code in pathways)
dfil = pd.read_csv('/Users/sarahbuchhorn/Desktop/cmap_wfh/urbansim/acs_bld_data/df55_units.csv')
dfil['pct1'] = dfil['B25024_002E'] / dfil['B25024_001E']
dfil['pct2'] = dfil['B25024_003E'] / dfil['B25024_001E']
dfil['pct3'] = dfil['B25024_004E'] / dfil['B25024_001E']
dfil['pct4'] = dfil['B25024_005E'] / dfil['B25024_001E']
dfil['pct5'] = dfil['B25024_006E'] / dfil['B25024_001E']
dfil['pct6'] = dfil['B25024_007E'] / dfil['B25024_001E']
dfil['pct7'] = dfil['B25024_008E'] / dfil['B25024_001E']
dfil['pct8'] = dfil['B25024_009E'] / dfil['B25024_001E']
dfil['pct9'] = dfil['B25024_010E'] / dfil['B25024_001E']
dfil['pct10'] = dfil['B25024_011E'] / dfil['B25024_001E']

def makejoinid(x):
    return str(x['state']) + str(x['county']).zfill(3) + str(x['tract']).zfill(5)

dfil['joinid'] = dfil.apply(makejoinid, axis=1)
dfil.to_csv('/Users/sarahbuchhorn/Desktop/cmap_wfh/urbansim/acs_bld_data/df55_pcts.csv')


# joing this data to block centroids
"""
From Noel's R script: 

external: 
BLK2ZN_FC <- arc.open("S:/Projects/LandUseModel/datadev/popsyn/controls_PBHI2010_zones17/controls_2010.gdb/CensusBlocks_ExternalArea_Centroids_byZone17")
blk2zn <- arc.select(object=BLK2ZN_FC,
                     fields=c("GEOID10", "GEOID10_TRACT", "subzone17", "zone17"),
                     where_clause="IN_7CO = 0")
blk2zn <- as_tibble(blk2zn) %>%
  mutate(MAZ = subzone17,
         TAZ = zone17,
         Block = GEOID10,
         Tract = GEOID10_TRACT,
         county_fips = substr(GEOID10, 1, 5)) %>%
  select(Block, Tract, county_fips, MAZ, TAZ)
  
internal is using the pbhi layer
PBHI_FC <- arc.open("S:/Projects/LandUseModel/datadev/popsyn/controls_PBHI2010_zones17/controls_2010.gdb/PBHI_2010_subzones17")

"""
######## bld controls from ACS tracts
internal = pd.read_csv("D:/2010lakecountypop/bld_control/pbhi2010subzones17.csv")
internal_col = internal[['Tract','HH_FIN','subzone17','zone17']]

# this is the ACS file with BLD category distribution for each category (number in category / total for tract)
distribution = pd.read_excel("D:/2010lakecountypop/bld_control/hhtype_dist.xlsx", sheet_name='df17_units')
distribution_pct = distribution[['joinid','pct1','pct2','pct3','pct4','pct5','pct6','pct7','pct8','pct9','pct10']]

# INTERNAL
internal_distribution = internal_col.merge(distribution_pct, left_on='Tract', right_on='joinid')

# the numbering was changed to match the PUMS bld number scheme
internal_distribution['num2'] = internal_distribution['pct1'] * internal_distribution['HH_FIN']
internal_distribution['num3'] = internal_distribution['pct2'] * internal_distribution['HH_FIN']
internal_distribution['num4'] = internal_distribution['pct3'] * internal_distribution['HH_FIN']
internal_distribution['num5'] = internal_distribution['pct4'] * internal_distribution['HH_FIN']
internal_distribution['num6'] = internal_distribution['pct5'] * internal_distribution['HH_FIN']
internal_distribution['num7'] = internal_distribution['pct6'] * internal_distribution['HH_FIN']
internal_distribution['num8'] = internal_distribution['pct7'] * internal_distribution['HH_FIN']
internal_distribution['num9'] = internal_distribution['pct8'] * internal_distribution['HH_FIN']
internal_distribution['num1'] = internal_distribution['pct9'] * internal_distribution['HH_FIN']
internal_distribution['num10'] = internal_distribution['pct10'] * internal_distribution['HH_FIN']



a = internal_distribution.groupby('subzone17').agg({'num1':'sum','num2':'sum','num3':'sum','num4':'sum',
                                                    'num5':'sum','num6':'sum','num7':'sum','num8':'sum',
                                                    'num9':'sum','num10':'sum'})

b = a.round(0)
b.to_csv("D:/2010lakecountypop/maz_bldg_controls2.csv")  # this is the tract-level distribution applied to maz


# EXTERNAL
external = pd.read_csv("D:/2010lakecountypop/bld_control/externalarea_centroids_z17.csv")

# get 1:1 tract/maz correspondence - keep only tract with highest count
c = external.groupby('subzone17').GEOID10_TRACT.value_counts().rename('tractcount').reset_index()
d = c.sort_values(by=['subzone17','tractcount'],ascending=[True,False])
e = d.drop_duplicates('subzone17',keep='first')
e.to_csv("D:/2010lakecountypop/bld_control/external_maz_tract.csv")

# add HH totals from maz controls (popsim run data folder)
mazcontrols = pd.read_csv("D:/2010lakecountypop/popsim16_failed2/data/control_totals_maz.csv")
e = e.merge(mazcontrols[['MAZ','HH']],left_on='subzone17',right_on='MAZ')
external_distribution = e.merge(distribution_pct,left_on='GEOID10_TRACT',right_on='joinid')

# the numbering was changed to match the PUMS bld number scheme (
external_distribution['num2'] = external_distribution['pct1'] * external_distribution['HH']
external_distribution['num3'] = external_distribution['pct2'] * external_distribution['HH']
external_distribution['num4'] = external_distribution['pct3'] * external_distribution['HH']
external_distribution['num5'] = external_distribution['pct4'] * external_distribution['HH']
external_distribution['num6'] = external_distribution['pct5'] * external_distribution['HH']
external_distribution['num7'] = external_distribution['pct6'] * external_distribution['HH']
external_distribution['num8'] = external_distribution['pct7'] * external_distribution['HH']
external_distribution['num9'] = external_distribution['pct8'] * external_distribution['HH']
external_distribution['num1'] = external_distribution['pct9'] * external_distribution['HH']
external_distribution['num10'] = external_distribution['pct10'] * external_distribution['HH']

a = external_distribution.groupby('subzone17').agg({'num1':'sum','num2':'sum','num3':'sum','num4':'sum',
                                                    'num5':'sum','num6':'sum','num7':'sum','num8':'sum',
                                                    'num9':'sum','num10':'sum'})

b = a.round(0)
b.to_csv("D:/2010lakecountypop/maz_ext_bldg_controls2.csv")  # this is the tract-level distribution applied to maz

# for tracts where we don't have building data, that will be it
# where there is building data, use that instead

######## blg controls from building file
buildings = pd.read_csv("C:/Users/sbuchhorn/Desktop/2010pop/buildings/lake/current/lakebuildingsextraatts_2.csv")
buildings = pd.read_csv("C:/Users/sbuchhorn/Desktop/2010pop/buildings/dupage/dupagebuildingsextraatts.csv")
buildings = pd.read_csv("C:/Users/sbuchhorn/Desktop/2010pop/buildings/cook/cookbuildingsextraatts.csv")
buildings = pd.read_csv("C:/Users/sbuchhorn/Desktop/2010pop/buildings/will/willbuildingsextraatts.csv")
buildings = pd.read_csv("C:/Users/sbuchhorn/Desktop/2010pop/buildings/kane/kanebuildingsextraatts.csv")
buildings = pd.read_csv("C:/Users/sbuchhorn/Desktop/2010pop/buildings/kendall/kendallbuildingsextraatts.csv")
buildings = pd.read_csv("C:/Users/sbuchhorn/Desktop/2010pop/buildings/mchenry/mchenrybuildingsextraatts.csv")

# summary of residential units by maz
buildings_types = buildings.groupby(['subzone17','classbldg']).agg({'residential_units':'sum'}).unstack().fillna(0).reset_index()
buildings_types.columns = buildings_types.columns.droplevel()
buildings_types.rename({'':'maz'}, axis=1, inplace=True)
buildings_types['total'] = buildings_types.iloc[:, 1:11].sum(axis=1)
# this (below) is the percentage of total in each category (from buildings file)
buildings_types.iloc[:,1:10] # check this is what you want (if there are no group0 this will be different)
buildings_types.iloc[:,1:10] = buildings_types.iloc[:,1:10].divide(buildings_types['total'], axis='index')
# should check if there are any maz where the buildings are mostly in 0, and if we can fix them
buildings_types[0].value_counts()   # percent of buildings that are 0
buildings_types.to_clipboard()

# great!  now bring in the tract
internalmaztract = pd.read_csv("D:/2010lakecountypop/bld_control/internal_maz_tract.csv")
x = buildings_types.merge(internalmaztract[['subzone17', 'Tract']], left_on='maz', right_on='subzone17')
# bring in HH counts
mazhh = pd.read_csv("D:/2010lakecountypop/bld_control/bldjustfromtract.csv")
mazhh['HHno0'] = mazhh['HH'] - mazhh['num11']  # count without the people not in buildings (group 10 in ACS/11 here)
buildings_types = x.merge(mazhh[['MAZ','HH','HHno0']], left_on='subzone17', right_on='MAZ')
# below, now we are making the building distribution match the HH total
buildings_types.iloc[:, 1:10] # check
buildings_types.iloc[:, 1:10] = buildings_types.iloc[:, 1:10].multiply(buildings_types['HHno0'], axis='index')
# so this is the building controls from buildings (assume households are distributed as the household building types are distributed)
blgControls = buildings_types
blgControls.to_csv("C:/Users/sbuchhorn/Desktop/2010pop/buildings/mchenry/buildingcontrolsfrombuildings_mchenry.csv")


# to get the factors...
# get the tract dist from before at the tract level (D:\2010lakecountypop\bld_control\distribution_pct from before)
     # (this is what we applied to the maz totals before to get controls for counties where we don't have bld data from noel)
distribution_pct_df = pd.read_csv("D:/2010lakecountypop/bld_control/distribution_pct.csv")
# then group the maz by the tract level and get a number of hh
tract_hh = blgControls.groupby('Tract').agg({'HHno0':'sum'}).reset_index()
# then get a number of hh in each bin based on the tract distribution (tract level)
tract_w_hh = distribution_pct_df.merge(tract_hh, left_on='joinid', right_on='Tract')
tract_w_hh.iloc[:, 1:11]
tract_w_hh.iloc[:, 1:11] = tract_w_hh.iloc[:, 1:11].multiply(tract_w_hh['HHno0'], axis='index')
# then compare this number to the tract total based on the building distribution
tractTotalsFromBlg = blgControls.groupby('Tract').agg({
    #0:'sum',
    1:'sum',
    2:'sum',3:'sum',4:'sum',5:'sum',6:'sum',7:'sum',8:'sum',9:'sum'}).reset_index()
compdf = tract_w_hh.merge(tractTotalsFromBlg, on='Tract')
# note that the pct are labelled by order (see original list line 26) while compdf are labelled by blgtype
compdf['twoF'] = compdf['pct1'] / compdf[2]
compdf['threeF'] = compdf['pct2'] / compdf[3]
compdf['fourF'] = compdf['pct3'] / compdf[4]
compdf['fiveF'] = compdf['pct4'] / compdf[5]
compdf['sixF'] = compdf['pct5'] / compdf[6]
compdf['sevenF'] = compdf['pct6'] / compdf[7]
compdf['eightF'] = compdf['pct7'] / compdf[8]
compdf['nineF'] = compdf['pct8'] / compdf[9]
compdf['oneF'] = compdf['pct9'] / compdf[1]

factors = compdf[['joinid','twoF','threeF','fourF','fiveF','sixF','sevenF','eightF','nineF',
                  'oneF'
                  ]]
# then obtain factors for each bin and each tract

#factoring the building controls to the tract distribution totals
#pd.options.display.float_format = '{:.2f}'.format
#factors = pd.read_csv("D:/2010lakecountypop/bld_control/dupage/bld_controls_factors_dp.csv")

a = blgControls.merge(factors,left_on='Tract',right_on='joinid')

# then multiply the building controls from buildings by the right factor
a['twon'] = a[2] * a['twoF']
a['threen'] = a[3] * a['threeF']
a['fourn'] = a[4] * a['fourF']
a['fiven'] = a[5] * a['fiveF']
a['sixn'] = a[6] * a['sixF']
a['sevenn'] = a[7] * a['sevenF']
a['eightn'] = a[8] * a['eightF']
a['ninen'] = a[9] * a['nineF']
a['onen'] = a[1] * a['oneF']
# we need different treatment for zero, because the zero coded buildings are
# just unclassified buildings, whereas the zero coded from ACS (#10) are boat, RV, van, etc.
# maybe we just take the tract distribution applied to maz and toss it in at the end, then let program
# sort it out?

#b = a.iloc[:,27:37].round(0)
b = a[['maz','HHno0','Tract','twon','threen','fourn','fiven','sixn','sevenn','eightn','ninen',
       'onen'
       ]].round(0)

b.to_csv("D:/2010lakecountypop/bld_control/lake/bld_controls_multiplied_lake.csv",index=False)
b.to_csv("D:/2010lakecountypop/bld_control/dupage/bld_controls_multiplied_dp.csv",index=False)
b.to_csv("D:/2010lakecountypop/bld_control/will/bld_controls_multiplied_will.csv",index=False)
b.to_csv("D:/2010lakecountypop/bld_control/kanekendall/bld_controls_multiplied_kane.csv",index=False)
b.to_csv("D:/2010lakecountypop/bld_control/kanekendall/bld_controls_multiplied_kendall.csv",index=False)
b.to_csv("D:/2010lakecountypop/bld_control/mchenry/bld_controls_multiplied_mchenry.csv",index=False)


# then rescale to make sure that each maz HH is still the right number

b['sum'] = b.iloc[:, 3:12].sum(axis=1)
b['scale'] = b['HHno0'] / b['sum']
b.iloc[:,3:12]
b.iloc[:,3:12] = b.iloc[:,3:12].multiply(b['scale'], axis='index')
b.iloc[:,3:12] = b.iloc[:,3:12].round(0)
b['sum'] = b.iloc[:,3:12].sum(axis=1)
# then fix the ones that are like +/- 1 or 2 off because of rounding
b['fix'] = b['sum'] - b['HHno0']
# just fold the strays into group 2 unless there are no 2s
b.loc[b['twon'] != 0, 'twon'] = b['twon'] - b['fix']
b['sum'] = b.iloc[:,3:12].sum(axis=1)
b['fix'] = b['sum'] - b['HHno0']

# i'm saving/working with them in file:///D:\2010lakecountypop\bld_control\master_bld_control_wb.xlsx
b.to_clipboard()