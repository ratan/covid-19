##############################################################################
# Praser for Covid-19
# Data Source
#   European Centre for Disease Prevention and Control (ECDC)
#   https://www.ecdc.europa.eu/en/publications-data/download-todays-data-geographic-distribution-covid-19-cases-worldwide
#   
# How to Use:
# Create Virtual Environment
# source covid19VirEnv/bin/activate
# python3 covid19ECDCProfiler.py COVID-19*.xls --country=China --all
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

parser=argparse.ArgumentParser(
        description='''Parse the excel sheet https://www.ecdc.europa.eu/en/publications-data/download-todays-data-geographic-distribution-covid-19-cases-worldwide ''',
        epilog="""the generated graphs will be stored in the folder""")
parser.add_argument('FILENAME',metavar='FILE',help='Filename of your exel sheet')
parser.add_argument('--country', action='store',nargs=1,type=str, help='Parse for a country e.g: --country=India')
parser.add_argument('--all', help='Prase for all the country e.g --all=True', action='store_true')
args = parser.parse_args()

#excel sheet name
fname = args.FILENAME

#https://stackoverflow.com/questions/36235559/how-to-use-python-to-read-one-column-from-excel-file
#df = pd.ExcelFile('./COVID-19-geographic-disbtribution-worldwide-2020-03-12.xls').parse('CSV_4_COMS') #you could add index_col=0 if there's an index
#df = pd.ExcelFile(fname).parse('CSV_4_COMS') #you could add index_col=0 if
#CountryExpDf=[]
#CountryExpDf.append(df['CountryExp'])
#print (CountryExpDf)
#columns
# DateRep   CountryExp  NewConfCases  NewDeaths GeoId Gaul1Nuts1          EU
dfCovidExcel = pd.read_excel(fname) 
#print (dfCovidExcel)
TotalCasesWW = dfCovidExcel['NewConfCases'].sum()
TotalDeathsWW = dfCovidExcel['NewDeaths'].sum()

fHTML = open('covid19_ECDC.html', 'w')
fHTML.write('<html>')
fHTML.write('<body>')
fHTML.write('<p>')
fHTML.write('<b>Raw data shared by ECDC (European Centre for Disease Prevention and Control)</b>')
fHTML.write('<p>')
if (args.country):
    checkCountry = args.country[0]
    #print ("Country Name: ",checkCountry)
    fHTML.write(f'Country Name:  {checkCountry}')
    fHTML.write('<p>')
    dfCountry = dfCovidExcel.loc[dfCovidExcel['CountryExp'] == checkCountry]
    #print (dfCountry)

    #Reverse Pandas Dataframe by Row
    #So that older dates are at top, and newer dates are at bottom
    dfCountry = dfCountry.iloc[::-1]
    #print (dfCountry)

    #plt.plot(dfCountry['DateRep'], dfCountry['NewConfCases'])
    #plt.show()
    MaxNewCase=dfCountry.loc[dfCountry['NewConfCases'].idxmax()]
    #print ("Max New Case in a day: Date ", MaxNewCase.DateRep, " Case: ",MaxNewCase.NewConfCases)
    fHTML.write('<p>')
    fHTML.write(f'Max New Case in a day: Date {MaxNewCase.DateRep}  Case:  {MaxNewCase.NewConfCases}')

    MaxNewDeaths=dfCountry.loc[dfCountry['NewDeaths'].idxmax()]
    #print ("Max Deaths in a day: Date ", MaxNewDeaths.DateRep, " Case: ",MaxNewDeaths.NewDeaths)
    fHTML.write('<p>')
    fHTML.write(f'Max Deaths in a day: Date {MaxNewDeaths.DateRep}  Case:  {MaxNewDeaths.NewDeaths}')

    TotalCases=dfCountry['NewConfCases'].sum()
    TotalDeaths=dfCountry['NewDeaths'].sum()

    #Find cumulative sum
    #Copy columns NewConfCases and NewDeaths
    dfCountryPlot = dfCountry[['NewConfCases', 'NewDeaths']].copy()
    dfCountryPlot = dfCountryPlot.cumsum(skipna=True)
    #print ("dfCountryPlot: ",dfCountryPlot)

    #Since cumulative sum for date will be wrong, i is taken from dfCountry
    #plt.plot(dfCountry['DateRep'], dfCountryPlot['NewConfCases'], linewidth=2)
    #plt.plot(dfCountry['DateRep'], dfCountryPlot['NewDeaths'], linewidth=2, linestyle='--')
    #plt.xticks(np.arange(min(dfCountry['DateRep']), max(dfCountry['DateRep']), 1.0))
    #plt.show()

    fig, ax = plt.subplots()
    ax.plot(dfCountry['DateRep'], dfCountryPlot['NewConfCases'], linewidth=2, label='Total Cases')
    ax.plot(dfCountry['DateRep'], dfCountryPlot['NewDeaths'], linewidth=2, linestyle='--', label='Total Deaths')
    ax.legend() #Add a legend
    tmpfile = BytesIO()
    fig.savefig(tmpfile, format='png')
    encoded = base64.b64encode(tmpfile.getvalue()).decode('utf-8')
    html = '<p>Chart for Total Cases and Total Deaths' + '<img src=\'data:image/png;base64,{}\'>'.format(encoded) + '</p>'
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
checkAllCountry=args.all
#print (checkAllCountry)
if (checkAllCountry==True):
    #print (dfCovidExcel.CountryExp.unique())
    countryList = dfCovidExcel.CountryExp.unique()
    #print ("No of Countries: ",len(countryList))
    fHTML.write('<p>')
    fHTML.write(f'No of Countries: {len(countryList)}')
    dfFinal = pd.DataFrame(columns=['Country', 'Total Cases', ' Total Deaths', '% Death', 'Max Case a day', 'Max Death a day' ])
    count = 0
    for myList in countryList:
        dfCountry = dfCovidExcel.loc[dfCovidExcel['CountryExp'] == myList]
        dfCountry.fillna(0) #Replace all na/null data with 0
        MaxNewCase=dfCountry.loc[dfCountry['NewConfCases'].idxmax()]
        MaxNewDeaths=dfCountry.loc[dfCountry['NewDeaths'].idxmax()]
        TotalCases=dfCountry['NewConfCases'].sum()
        TotalDeaths=dfCountry['NewDeaths'].sum()
        percDeath = (TotalDeaths *100.00)/TotalCases
        #print ("Country: ", myList, "Total cases: ",TotalCases, "Total deaths: ", TotalDeaths)
        dfFinal.loc[count] = [myList, TotalCases, TotalDeaths, percDeath, MaxNewCase.NewConfCases, MaxNewDeaths.NewDeaths]
        count = count + 1
    #dfFinal.sort_values(by='Total Cases', ascending=False, inplace=True)
    dfFinalCopy = dfFinal.sort_values(by='Total Cases', ascending=False, ignore_index=True)
    #print (dfFinal)
    #print (dfFinalCopy)
    fHTML.write('<p>')
    dfFinalCopy.to_html(fHTML)
    #with open('covid19.html', 'w') as fo:
        #dfFinalCopy.to_html(fo)

fHTML.write('</body>')
fHTML.write('</html>')
