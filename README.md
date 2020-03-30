# covid-19
Parser for covid-19
Raw Data shared by: European Centre for Disease Prevention and Control (ECDC) 
Link: https://www.ecdc.europa.eu/en/publications-data/download-todays-data-geographic-distribution-covid-19-cases-worldwide

Steps to create a virtual environment:
--------------------------------------
1. Find out Python3 version:
python3 -V

2. It should output something like:
Python 3.7.4

3.If required
sudo apt install virtualenv

4. Now run the following command to create a virtual environment
virtualenv --no-site-packages --python=python3.7 covid19VirEnv

5. To activate the the virtual environment run
source covid19VirEnv/bin/activate

6. To install dependencies run
pip3 install pandas matplotlib tabulate plotly xlrd


Steps to Run Covid Profiler:
--------------------------
1. To activate the the virtual environment run
source covid19VirEnv/bin/activate

2. To generate the graphs run
python3 covid19ECDCProfiler.py <logFileName>

python3 covid19ECDCProfiler.py --country=China
  country: input country name for which you want to see details data (optional parameter)

Output:
--------------------------
1. Output HTML file (covid19_ECDC_<YYYY-MM-DD>.html) is generated, which has all the data in tabular/text format.

Limitations:
--------------------------
1. Tested in Ubuntu 18.08 only
2. The raw data excel sheet needs minor modification. Some of the entries in column NewDeaths is empty. Fill them with 0
(Select filter next to the NewDeaths column, remove selection againt "Select All", select "Blanc". Now fill 0 (zero) againt all the blanc cells. Now click on the filter, and select all to bring it back to original view. Save the excel sheet)

3. covid19ECDCProfiler_16Mar.py works with excel sheet 16 March and previous  dates
covid19ECDCProfiler.py works with excel sheet 17 March and latest


--------------------------
Windows Setup
--------------------------
1. Create Virtual env
virtualenv --python=python3.8 covid19VirEnv

2. To activate the the virtual environment run
covid19VirEnv\Scripts\activate

3. To install dependencies run
pip install pandas matplotlib tabulate plotly xlrd requests

4. deactivate
deactivate

Steps to Run Covid Profiler:
--------------------------
1. To activate the the virtual environment run
covid19VirEnv\Scripts\activate

2. To generate the graphs run
python covid19ECDCProfiler.py --country=China

--country parameter is optional.
