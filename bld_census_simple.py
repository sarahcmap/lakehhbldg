#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Get maz-level BLD data from our own building file, and use this information along with
ACS tract-level building type data to get building controls for new populationsim runs.

Note the assumption that households are distributed as the household building types are distributed.
"""
import pandas as pd


######## blg controls from building file
buildings = pd.read_csv("/Users/sarahbuchhorn/Desktop/cmap_wfh/urbansim/counties/kane/kanebuildingsextraatts_v1.csv")
buildings = pd.read_csv("C:/Users/sbuchhorn/Desktop/2010pop/buildings/dupage/dupagebuildingsextraatts.csv")
buildings = pd.read_csv("C:/Users/sbuchhorn/Desktop/2010pop/buildings/cook/cookbuildingsextraatts.csv")
buildings = pd.read_csv("C:/Users/sbuchhorn/Desktop/2010pop/buildings/will/willbuildingsextraatts.csv")
buildings = pd.read_csv("C:/Users/sbuchhorn/Desktop/2010pop/buildings/kane/kanebuildingsextraatts.csv")
buildings = pd.read_csv("C:/Users/sbuchhorn/Desktop/2010pop/buildings/kendall/kendallbuildingsextraatts.csv")
buildings = pd.read_csv("C:/Users/sbuchhorn/Desktop/2010pop/buildings/mchenry/mchenrybuildingsextraatts.csv")

# summary of residential units by maz
buildings_types = buildings.groupby(['subzone17', 'classbldg']).agg({'residential_units': 'sum'}).unstack().fillna(
    0).reset_index()
buildings_types.columns = buildings_types.columns.droplevel()
buildings_types.rename_axis({'': 'maz'}, axis=1, inplace=True)
buildings_types['total'] = buildings_types.iloc[:, 1:11].sum(axis=1)
# this (below) is the percentage of total in each category (from buildings file)
buildings_types.iloc[:, 1:10]  # check this is what you want (if there are no group0 this will be different)
buildings_types.iloc[:, 1:10] = buildings_types.iloc[:, 1:10].divide(buildings_types['total'], axis='index')
# should check if there are any maz where the buildings are mostly in 0, and if we can fix them
buildings_types[0].value_counts()  # percent of buildings that are 0
buildings_types.to_clipboard()

# great!  now bring in the tract
internalmaztract = pd.read_csv('/Users/sarahbuchhorn/Desktop/cmap_wfh/Desktop Copy/bld_control/internal_maz_tract.csv')
x = buildings_types.merge(internalmaztract[['subzone17', 'Tract']], left_on='maz', right_on='subzone17')
# bring in HH counts
# use the hh totals from futurepop 2010 run
mazhh = pd.read_csv("/Users/sarahbuchhorn/Desktop/cmap_wfh/urbansim/popsim25/data/control_totals_maz.csv")
# grab just the sz that you want
mazhhcounty = mazhh[(mazhh['MAZ'] >= 5253) & (mazhh['MAZ'] <= 7406)]
mazhhcounty['HHno0'] = mazhhcounty['HH'] - mazhhcounty[
    'num10']  # count without the people not in buildings (group 10 in ACS/11 here)
buildings_types = x.merge(mazhhcounty[['MAZ', 'HH', 'HHno0']], left_on='subzone17', right_on='MAZ', how='right')
# below, now we are making the building distribution match the HH total
buildings_types.iloc[:, 1:10]  # check
buildings_types.iloc[:, 1:10] = buildings_types.iloc[:, 1:10].multiply(buildings_types['HHno0'], axis='index')
# so this is the building controls from buildings (assume households are distributed as the household building types are distributed)
blgControls = buildings_types
blgControls.to_csv(
    "/Users/sarahbuchhorn/Desktop/cmap_wfh/urbansim/counties/kane/buildingcontrolsfrombuildings_kanetest.csv")

# to get the factors...
# get the tract dist from before at the tract level (D:\2010lakecountypop\bld_control\distribution_pct from before)
# (this is what we applied to the maz totals before to get controls for counties where we don't have bld data from noel)
distribution_pct_df = pd.read_csv("/Users/sarahbuchhorn/Desktop/cmap_wfh/Desktop Copy/bld_control/distribution_pct.csv")
# then group the maz by the tract level and get a number of hh
tract_hh = blgControls.groupby('Tract').agg({'HHno0': 'sum'}).reset_index()
# then get a number of hh in each bin based on the tract distribution (tract level)
tract_w_hh = distribution_pct_df.merge(tract_hh, left_on='joinid', right_on='Tract')
tract_w_hh.iloc[:, 1:11]
tract_w_hh.iloc[:, 1:11] = tract_w_hh.iloc[:, 1:11].multiply(tract_w_hh['HHno0'], axis='index')
# then compare this number to the tract total based on the building distribution
tractTotalsFromBlg = blgControls.groupby('Tract').agg({
    # 0:'sum',
    1: 'sum',
    2: 'sum', 3: 'sum', 4: 'sum', 5: 'sum', 6: 'sum', 7: 'sum', 8: 'sum', 9: 'sum'}).reset_index()
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

factors = compdf[['joinid', 'twoF', 'threeF', 'fourF', 'fiveF', 'sixF', 'sevenF', 'eightF', 'nineF',
                  'oneF'
                  ]]
# then obtain factors for each bin and each tract

# factoring the building controls to the tract distribution totals
# pd.options.display.float_format = '{:.2f}'.format
# factors = pd.read_csv("D:/2010lakecountypop/bld_control/dupage/bld_controls_factors_dp.csv")

a = blgControls.merge(factors, left_on='Tract', right_on='joinid', how='left')

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

# b = a.iloc[:,27:37].round(0)
b = a[['maz', 'MAZ', 'HH', 'HHno0', 'Tract', 'twon', 'threen', 'fourn', 'fiven', 'sixn', 'sevenn', 'eightn', 'ninen',
       'onen'
       ]].round(0)

b.to_csv("/Users/sarahbuchhorn/Desktop/cmap_wfh/urbansim/counties/kane//bld_controls_multiplied_kane_test.csv",
         index=False)
b.to_csv("D:/2010lakecountypop/bld_control/dupage/bld_controls_multiplied_dp.csv", index=False)
b.to_csv("D:/2010lakecountypop/bld_control/will/bld_controls_multiplied_will.csv", index=False)
b.to_csv("D:/2010lakecountypop/bld_control/kanekendall/bld_controls_multiplied_kane.csv", index=False)
b.to_csv("D:/2010lakecountypop/bld_control/kanekendall/bld_controls_multiplied_kendall.csv", index=False)
b.to_csv("D:/2010lakecountypop/bld_control/mchenry/bld_controls_multiplied_mchenry.csv", index=False)

# then rescale to make sure that each maz HH is still the right number

b['sum'] = b.iloc[:, 5:14].sum(axis=1)
b['scale'] = b['HHno0'] / b['sum']
b.iloc[:, 5:14]
b.iloc[:, 5:14] = b.iloc[:, 5:14].multiply(b['scale'], axis='index')
b.iloc[:, 5:14] = b.iloc[:, 5:14].round(0)
b['sum'] = b.iloc[:, 5:14].sum(axis=1)
# then fix the ones that are like +/- 1 or 2 off because of rounding
b['fix'] = b['sum'] - b['HHno0']
# just fold the strays into group 2 unless there are no 2s
b.loc[b['twon'] != 0, 'twon'] = b['twon'] - b['fix']
b['sum'] = b.iloc[:, 5:14].sum(axis=1)
b['fix'] = b['sum'] - b['HHno0']

# i'm saving/working with them in file:///D:\2010lakecountypop\bld_control\master_bld_control_wb.xlsx
b.to_clipboard()