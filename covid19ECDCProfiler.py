##############################################################################
# Praser for Covid-19
# Data Source
#   European Centre for Disease Prevention and Control (ECDC)
#   https://www.ecdc.europa.eu/en/publications-data/download-todays-data-geographic-distribution-covid-19-cases-worldwide
#   
# How to Use:
# Create Virtual Environment
# source covid19VirEnv/bin/activate
# python3 covid19ECDCProfiler.py --country=China
# It will generated html file
##############################################################################



import pandas as pd
import matplotlib
matplotlib.use('TkAgg')
import numpy as np
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings('ignore')
import sys
import os
import argparse
import gc
from collections import Counter
gc.collect()
from tabulate import tabulate
import plotly
import plotly.graph_objs as go
import base64
from io import BytesIO
import datetime
import requests

parser=argparse.ArgumentParser(
        description='''Parse the excel sheet https://www.ecdc.europa.eu/sites/default/files/documents/COVID-19-geographic-disbtribution-worldwide-2020-03-24.xlsx ''',
        epilog="""the generated graphs will be stored in the folder""")
parser.add_argument('--country', action='store',nargs=1,type=str, help='Parse for a country e.g: --country=India')
args = parser.parse_args()

#https://www.geeksforgeeks.org/downloading-files-web-using-python/
#check for filename
#ECDC file name : https://www.ecdc.europa.eu/sites/default/files/documents/COVID-19-geographic-disbtribution-worldwide-2020-03-24.xlsx
#print(datetime.datetime.now())
myDate = datetime.datetime.now()
#print (myDate)
myDateCustom = (str(myDate)).split( ) #split the string by space, ' '
#print(myDateCustom[0]) #from 2020-03-24 16:39:02.038854 to 2020-03-24

fileECDCName = "COVID-19-geographic-disbtribution-worldwide-" + myDateCustom[0] + ".xlsx"
#print(fileECDCName)
# URL of the excel to be downloaded is defined as excel_url
excel_url = "https://www.ecdc.europa.eu/sites/default/files/documents/" + fileECDCName

# Check if the URL exist. Otherwise ECDC has excel sheet for yesterday's date only.
# Send a HTTP request to the server and save the HTTP response
# in a response object called r
r = requests.get(excel_url) #create HTTP response object
#if r.status_code == 200:
#    print('Web site exists')
#else:
if r.status_code != 200:
    #print('Web site does not exist')
    #Get 1 day back date
    lastHourDateTime = datetime.datetime.now() - datetime.timedelta(days = 1)
    #print (lastHourDateTime)
    myDateCustom = (str(lastHourDateTime)).split( ) #split the string by space, ' '
    #print(myDateCustom[0])
    fileECDCName = "COVID-19-geographic-disbtribution-worldwide-" + myDateCustom[0] + ".xlsx"
    excel_url = "https://www.ecdc.europa.eu/sites/default/files/documents/" + fileECDCName

#Remove the existing excel file
#os.remove(fileECDCName)

print ("File from ECDC :", excel_url)
# Send the HTTP request again
r = requests.get(excel_url) #create HTTP response object

# Save received content as a excel file in binary format
# Write the contents of the response (r.content) to a new file
#with open("COVID-19-geographic-disbtribution-worldwide.xlsx", 'wb') as fExcel:
with open(fileECDCName, 'wb') as fExcel:
    fExcel.write(r.content)

dfCovidExcel = pd.read_excel(fileECDCName)
#print (dfCovidExcel)

#Make day and month column 2 digits, leading zero
#https://stackoverflow.com/questions/23836277/add-leading-zeros-to-strings-in-pandas-dataframe
dfCovidExcel['day'] = dfCovidExcel['day'].apply(lambda x: '{0:0>2}'.format(x))
dfCovidExcel['month'] = dfCovidExcel['month'].apply(lambda x: '{0:0>2}'.format(x))

#Add a new column, 'date' at the end, which will be month+day (concat)
#month=03, day=25 will become 0325
dfCovidExcel['date'] = (dfCovidExcel['month']) + (dfCovidExcel['day'])
#print (dfCovidExcel) #updated DF with new column

TotalCasesWW = dfCovidExcel['cases'].sum()
TotalDeathsWW = dfCovidExcel['deaths'].sum()

myHtmlOut = "covid19_ECDC_" + myDateCustom[0] + ".html"
#fHTML = open('covid19_ECDC.html', 'w')
fHTML = open(myHtmlOut, 'w')
fHTML.write('<html>')
fHTML.write('<body>')
fHTML.write('<p>')
fHTML.write('<b>Raw data shared by ECDC (European Centre for Disease Prevention and Control)</b>')
fHTML.write('<p>')
fHTML.write('https://www.ecdc.europa.eu/en/publications-data/download-todays-data-geographic-distribution-covid-19-cases-worldwide')
fHTML.write('<p>')


if (args.country):
    checkCountry = args.country[0]
    #print ("Country Name: ",checkCountry)
    fHTML.write(f'<b> Details for country {checkCountry}</b>')
    fHTML.write('<p>')
    dfCountry = dfCovidExcel.loc[dfCovidExcel['countriesAndTerritories'] == checkCountry]
    #print (dfCountry)

    #Reverse Pandas Dataframe by Row
    #So that older dates are at top, and newer dates are at bottom
    dfCountry = dfCountry.iloc[::-1]
    #print (dfCountry)

    #plt.plot(dfCountry['DateRep'], dfCountry['fCases'])
    #plt.show()
    MaxCase=dfCountry.loc[dfCountry['cases'].idxmax()]
    #print ("Max Case in a day: Date ", MaxCase.DateRep, " Case: ",MaxCase.Cases)
    fHTML.write('<p>')
    fHTML.write(f'Max Case in a day: Date {MaxCase.date}  Case:  {MaxCase.cases}')

    MaxDeaths=dfCountry.loc[dfCountry['deaths'].idxmax()]
    #print ("Max Deaths in a day: Date ", MaxDeaths.DateRep, " Case: ",MaxDeaths.Deaths)
    fHTML.write('<p>')
    fHTML.write(f'Max Deaths in a day: Date {MaxDeaths.date}  Case:  {MaxDeaths.deaths}')

    TotalCases=dfCountry['cases'].sum()
    TotalDeaths=dfCountry['deaths'].sum()

    #Find cumulative sum
    #Copy columns Cases and Deaths
    dfCountryPlot = dfCountry[['date', 'cases', 'deaths']].copy()

    #Find the cumulative sum for Cases and Deaths columns only
    dfCountryPlot['cases'] = dfCountryPlot['cases'].cumsum()
    dfCountryPlot['deaths'] = dfCountryPlot['deaths'].cumsum()

    #dfCountryPlot = dfCountryPlot.cumsum(skipna=True)
    #Drop all the rows here cumulative Cases column values is 0, where no case was reported initially.
    dfCountryPlot.drop(dfCountryPlot[dfCountryPlot['cases'] <= 0].index, inplace = True) 
    #print ("dfCountryPlot: ")
    #print (dfCountryPlot)

    #Since cumulative sum for date will be wrong, x is taken from dfCountry and not from dfCountryPlot
    fig, ax = plt.subplots(figsize=(12, 6))
    # Don't allow the axis to be on top of your data
    ax.set_axisbelow(True)
    # Turn on the grid
    ax.grid()
    # Turn on the minor TICKS, which are required for the minor GRID
    ax.minorticks_on()
    # Customize the major grid
    ax.grid(which='major', linestyle='-', linewidth='0.5', color='red')
    # Customize the minor grid
    ax.grid(which='minor', linestyle=':', linewidth='0.5', color='black')
    ax.set_xlabel("Date [MMDD format]")
    ax.set_ylabel("Total Cases")
    ax.plot(dfCountryPlot['date'], dfCountryPlot['cases'], linewidth=2, label='Total Cases')
    every_nth = 5 #Tak every 5th tick in the plot
    for n, label in enumerate(ax.xaxis.get_ticklabels()):
        if n % every_nth != 0:
            label.set_visible(False)
    ax.legend() #Add a legend
    #Rotate x axis label by 90 degree
    for tick in ax.get_xticklabels():
        tick.set_rotation(90)
    tmpfile = BytesIO()
    fig.savefig(tmpfile, format='png')
    encoded = base64.b64encode(tmpfile.getvalue()).decode('utf-8')
    #html = '<p>Chart for Total Cases' + '<img src=\'data:image/png;base64,{}\'>'.format(encoded) + '</p>'
    fHTML.write(f'<p><b>Chart for Total Cases and Total Deaths for the country {checkCountry}</b>')
    html = '<img src=\'data:image/png;base64,{}\'>'.format(encoded)
    #plt.show()
    fHTML.write(html)

    fig1, ax1 = plt.subplots(figsize=(12, 6))
    # Don't allow the axis to be on top of your data
    ax1.set_axisbelow(True)
    # Turn on the grid
    ax1.grid()
    # Turn on the minor TICKS, which are required for the minor GRID
    ax1.minorticks_on()
    # Customize the major grid
    ax1.grid(which='major', linestyle='-', linewidth='0.5', color='red')
    # Customize the minor grid
    ax1.grid(which='minor', linestyle=':', linewidth='0.5', color='black')
    ax1.set_xlabel("Date [MMDD format]")
    ax1.set_ylabel("Total Deaths")
    ax1.plot(dfCountryPlot['date'], dfCountryPlot['deaths'], linewidth=2, linestyle='--', label='Total Deaths')
    every_nth = 5 #Tak every 5th tick in the plot
    for n, label in enumerate(ax1.xaxis.get_ticklabels()):
        if n % every_nth != 0:
            label.set_visible(False)
    ax1.legend() #Add a legend
    #Rotate x axis label by 90 degree
    for tick in ax1.get_xticklabels():
        tick.set_rotation(90)
    tmpfile = BytesIO()
    fig1.savefig(tmpfile, format='png')
    encoded = base64.b64encode(tmpfile.getvalue()).decode('utf-8')
    html = '<p><img src=\'data:image/png;base64,{}\'>'.format(encoded) + '</p>'
    #plt.show()
    fHTML.write(html)

    fHTML.write('<p>')
    fHTML.write(f'Total cases: {TotalCases}')
    fHTML.write('<p>')
    fHTML.write(f'Total deaths: {TotalDeaths}')
    #print ("Total cases: ",TotalCases)
    #print ("Total deaths: ",TotalDeaths)
    fHTML.write('</p>')

#print ("World Wide: Total cases: ",TotalCasesWW, " Total Deaths: ",TotalDeathsWW)
fHTML.write('<p>')
fHTML.write(f'<b>World Wide: Total cases: {TotalCasesWW} Total Deaths: {TotalDeathsWW}</b>')

#print (dfCovidExcel.Countries and territories.unique())
countryList = dfCovidExcel['countriesAndTerritories'].unique()
#print ("No of Countries: ",len(countryList))
fHTML.write('<p>')
fHTML.write(f'No of Countries: {len(countryList)}')

#create a empty DataFrame
dfFinal = pd.DataFrame(columns=['Country', 'Cases', 'Deaths', '% Death', 'Max Case a day', 'Max Death a day' ])
count = 0
for myList in countryList:
    dfCountry = dfCovidExcel.loc[dfCovidExcel['countriesAndTerritories'] == myList]
    dfCountry.fillna(0) #Replace all na/null data with 0
    MaxCase=dfCountry.loc[dfCountry['cases'].idxmax()]
    MaxDeaths=dfCountry.loc[dfCountry['deaths'].idxmax()]
    TotalCases=dfCountry['cases'].sum()
    TotalDeaths=dfCountry['deaths'].sum()
    percDeath = (TotalDeaths *100.00)/TotalCases
    #print ("Country: ", myList, "Total cases: ",Cases, "Deaths: ", TotalDeaths)
    dfFinal.loc[count] = [myList, TotalCases, TotalDeaths, percDeath, MaxCase.cases, MaxDeaths.deaths]
    count = count + 1
dfFinalCopy = dfFinal.sort_values(by='Cases', ascending=False, ignore_index=True)
#  Country  Cases Deaths    % Death Max Case a day Max Death a day
#0   China  81968   3293   4.017421          15141             254
#1   Italy  74386   7505  10.089264           6557             795

dfFinalCopy = dfFinalCopy.reset_index()
#     index   Country  Cases Deaths    % Death Max Case a day Max Death a day
#0        0     China  81968   3293   4.017421          15141             254
#1        1     Italy  74386   7505  10.089264           6557             795

#We dont want to print the index, but the column with name index.
#Also change the column name from index to SerialNum
#SerialNum is starting from 0, make the starting no 1
dfFinalCopy.rename(columns = {'index':'SerialNum'}, inplace = True)
dfFinalCopy.SerialNum = dfFinalCopy.SerialNum +1 
#print (dfFinalCopy.to_string(index=False))

fHTML.write('<p>')
dfFinalCopy.to_html(fHTML, index=False)


#Plot the graph for world
#Find cumulative sum
#Copy columns Cases and Deaths
dfWorldPlot = dfCovidExcel[['date', 'cases', 'deaths']].copy()
dfWorldPlot = dfWorldPlot.groupby('date').agg({'cases':'sum','deaths':'sum'})
#print (dfWorldPlot)

# 31 Dec 2019 (1231) row will come at the bottom. Add it with 0101 (Jan 01, 2020)
# and drop the row with date 1231
dfWorldPlot.loc['0101'] += dfWorldPlot.loc['1231']
dfWorldPlot.drop(['1231'], inplace=True)
#print (dfWorldPlot)

#Find the cumulative sum for Cases and Deaths columns only
dfWorldPlot['cases'] = dfWorldPlot['cases'].cumsum()
dfWorldPlot['deaths'] = dfWorldPlot['deaths'].cumsum()
#print (dfWorldPlot)

#Here Date is an index now due to groupby
#       Cases  Deaths
#Date
#0101      27       0
#0102      27       0
#0103      44       0
#0104      44       0
#0105      59       0

#We want to Convert index of a Dataframe into a column of dataframe
#Date      Cases  Deaths
#0101      27       0
#0102      27       0
#0103      44       0
#0104      44       0
#0105      59       0

#https://thispointer.com/pandas-convert-dataframe-index-into-column-using-dataframe-reset_index-in-python/
#Convert index to column
dfWorldPlot = dfWorldPlot.reset_index()
#print (dfWorldPlot)

#dfWorldPlot = dfWorldPlot.cumsum(skipna=True)
#Drop all the rows here cumulative Cases column values is 0, where no case was reported initially.
dfWorldPlot.drop(dfWorldPlot[dfWorldPlot['cases'] <= 0].index, inplace = True)
#print ("dfWorldPlot: ")
#print (dfWorldPlot)

#Since cumulative sum for date will be wrong, x is taken from dfCountry and not from dfWorldPlot
fig, ax = plt.subplots(figsize=(12, 6))
# Don't allow the axis to be on top of your data
ax.set_axisbelow(True)
# Turn on the grid
ax.grid()
# Turn on the minor TICKS, which are required for the minor GRID
ax.minorticks_on()
# Customize the major grid
ax.grid(which='major', linestyle='-', linewidth='0.5', color='red')
# Customize the minor grid
ax.grid(which='minor', linestyle=':', linewidth='0.5', color='black')
ax.set_xlabel("Date [MMDD format]")
ax.set_ylabel("Total Cases")
ax.plot(dfWorldPlot['date'], dfWorldPlot['cases'], linewidth=2, label='Total Cases')
every_nth = 5 #Tak every 5th tick in the plot
for n, label in enumerate(ax.xaxis.get_ticklabels()):
    if n % every_nth != 0:
        label.set_visible(False)
ax.legend() #Add a legend
#Rotate x axis label by 90 degree
for tick in ax.get_xticklabels():
    tick.set_rotation(90)
tmpfile = BytesIO()
fig.savefig(tmpfile, format='png')
encoded = base64.b64encode(tmpfile.getvalue()).decode('utf-8')
#html = '<p>World Chart for Total Cases' + '<img src=\'data:image/png;base64,{}\'>'.format(encoded) + '</p>'
fHTML.write('<p><b>World Wide Chart for Total Cases and Total Deaths</b>')
html = '<img src=\'data:image/png;base64,{}\'>'.format(encoded)
#plt.show()
fHTML.write(html)

fig1, ax1 = plt.subplots(figsize=(12, 6))
# Don't allow the axis to be on top of your data
ax1.set_axisbelow(True)
# Turn on the grid
ax1.grid()
# Turn on the minor TICKS, which are required for the minor GRID
ax1.minorticks_on()
# Customize the major grid
ax1.grid(which='major', linestyle='-', linewidth='0.5', color='red')
# Customize the minor grid
ax1.grid(which='minor', linestyle=':', linewidth='0.5', color='black')
ax1.set_xlabel("Date [MMDD format]")
ax1.set_ylabel("Total Deaths")
ax1.plot(dfWorldPlot['date'], dfWorldPlot['deaths'], linewidth=2, linestyle='--', label='Total Deaths')
every_nth = 5 #Tak every 5th tick in the plot
for n, label in enumerate(ax1.xaxis.get_ticklabels()):
    if n % every_nth != 0:
        label.set_visible(False)
ax1.legend() #Add a legend
#Rotate x axis label by 90 degree
for tick in ax1.get_xticklabels():
    tick.set_rotation(90)
tmpfile = BytesIO()
fig1.savefig(tmpfile, format='png')
encoded = base64.b64encode(tmpfile.getvalue()).decode('utf-8')
#html = '<p>World Chart for Total Deaths' + '<img src=\'data:image/png;base64,{}\'>'.format(encoded) + '</p>'
html = '<img src=\'data:image/png;base64,{}\'>'.format(encoded) + '</p>'
#plt.show()
fHTML.write(html)
    

fHTML.write('</body>')
fHTML.write('</html>')
