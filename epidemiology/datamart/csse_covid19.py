import io, os, shutil, errno
import pandas as pd
import numpy as np
from epidemiology.config import env_config as ENVCFG


def prepDir(dirpath):
  try:
    os.makedirs(dirpath)
  except Exception as ex:
    pass


def deleteDir(path):
  try:
    shutil.rmtree(path)
  except OSError as exc:  # Python >2.5
    if exc.errno == errno.ENOENT:
      pass
    else:
      raise


class CSSE_COVID19:
  @classmethod
  def setup(cls, clean=True):
    '''
    Setup data folders for all countries in the dataset
    :return: None
    '''

    # sync all datasets from their respective repos using data folder shell script
    os.system(' && '.join(['cd ' + ENVCFG.FILESYSTEM.DATA_ROOT,
                           'bash data_sync.sh'
                           ]))

    if clean:
      deleteDir(os.path.join(ENVCFG.FILESYSTEM.DATA_ROOT, 'kq'))
    # retrieve list of countries from on of the data files
    filepath = os.path.join(
      ENVCFG.FILESYSTEM.TIMESERIES_ROOTPATH, 'time_series_covid19_confirmed_global.csv'
    )
    dataDf = pd.read_csv(filepath, sep=',', header=0)
    countries = dataDf['Country/Region'].unique()

    # create data folders for all countries and for the aggregated world level data
    for country in countries:
      prepDir(os.path.join(ENVCFG.FILESYSTEM.DATA_ROOT, 'kq', country, 'national'))

    prepDir(os.path.join(ENVCFG.FILESYSTEM.DATA_ROOT, 'kq', 'WORLD'))


class COVID19_Country:
  '''
    Covid-19 Class for processing data at country & state/province granularity
  '''

  def __init__(self, country, countryDf, datapoint):
    '''
    Setup instance level params
    :param country: String, country for which timeseries needs to be processed
    :param countryDf: pandas.DataFrame, the country level raw timeseries data
    :param datapoint: String, the datapoint being processed (e.g. Confirmed, Deaths, Recovered)
    '''
    self.country = country
    self.countryDf = countryDf
    self.datapoint = datapoint

    # root path where country level processed data is stored
    self.countryDataRoot = os.path.join(ENVCFG.FILESYSTEM.DATA_ROOT, 'kq', self.country)

  @staticmethod
  def extractByState_fromCountryFiles(country):
    '''
    Extracts and processes timeseries data per state of the country specified in the data
    :return: pandas.DataFrame
    '''
    for datapoint in ['confirmed', 'deaths']:
      datafile = '_'.join(['time_series_covid19', datapoint, country]) + '.csv'
      filepath = os.path.join(ENVCFG.FILESYSTEM.TIMESERIES_ROOTPATH, datafile)
      dataDf = pd.read_csv(filepath, sep=',', header=0)
      dataDf.drop(['Country_Region', 'Lat', 'Long_'], axis=1, inplace=True)

      statesDf = dataDf.groupby(['Province_State']).sum()
      savepath = os.path.join(ENVCFG.FILESYSTEM.DATA_ROOT, 'kq', country, 'state', 'time_series_' + datapoint + '.csv')
      statesDf.to_csv(savepath)

  @staticmethod
  def extractByCounty_fromCountryFiles(country):
    '''
    Extracts and processes timeseries data per country of the country specified in the data
    :return: pandas.DataFrame
    '''

    for datapoint in ['confirmed', 'deaths']:
      datafile = '_'.join(['time_series_covid19', datapoint, country]) + '.csv'
      filepath = os.path.join(ENVCFG.FILESYSTEM.TIMESERIES_ROOTPATH, datafile)
      countyDf = pd.read_csv(filepath, sep=',', header=0)
      countyDf.drop(['Country_Region', 'Lat', 'Long_'], axis=1, inplace=True)
      countyDf.set_index('Admin2', inplace=True)
      savepath = os.path.join(ENVCFG.FILESYSTEM.DATA_ROOT, 'kq', country, 'county', 'time_series_' + datapoint + '.csv')
      countyDf.to_csv(savepath)

  def extractByState(self):
    '''
    Extracts and processes timeseries data per state of the country specified in the data
    :return: pandas.DataFrame
    '''
    countryStateDf = self.countryDf[~self.countryDf['Province/State'].str.contains(',')]
    countryStateDf.set_index('Province/State', inplace=True)
    countryStateDf.drop(['Country/Region'], axis=1, inplace=True)
    return countryStateDf

  def extractByCounty(self):
    '''
    Extracts and processes timeseries data per country of the country specified in the data
    :return: pandas.DataFrame
    '''
    countryCountyDf = self.countryDf[self.countryDf['Province/State'].str.contains(',')]
    countryCountyDf.set_index('Province/State', inplace=True)
    countryCountyDf.drop(['Country/Region'], axis=1, inplace=True)
    return countryCountyDf

  def extract(self, subregionsToExtract=['state', 'county']):
    '''
    Extracts and process timeseries data for the country
    :param subregionsToExtract: List, the different granularities at which to extract data for the country
    :return: List, timeseries aggregated for the country and datapoint specified at the time of initialisation
    '''

    # prepare data subdirectories for subregions
    for subdir in ['state', 'county']:
      if subdir in subregionsToExtract:
        prepDir(os.path.join(self.countryDataRoot, subdir))

    if self.countryDf.shape[0] == 1:  # no state and county level data present
      self.countryDf[2:].to_csv(
        os.path.join(self.countryDataRoot, 'national', 'time_series_' + self.datapoint + '.csv'))
      nationalTimeSeries = self.countryDf.drop(['Province/State', 'Country/Region'], axis=1)
    elif self.countryDf.shape[0] > 1:  # state and/or county level data present
      if 'county' in subregionsToExtract:
        countryCountyDf = self.extractByCounty()
        if countryCountyDf.shape[0] > 0:
          countryCountyDf.to_csv(os.path.join(self.countryDataRoot, 'county', 'time_series_' + self.datapoint + '.csv'))

      countryStatesDf = self.extractByState()
      if 'state' in subregionsToExtract:
        countryStatesDf.to_csv(os.path.join(self.countryDataRoot, 'state', 'time_series_' + self.datapoint + '.csv'))
      nationalTimeSeries = countryStatesDf.sum().to_frame().T

    nationalTimeSeries.to_csv(os.path.join(self.countryDataRoot, 'national', 'time_series_' + self.datapoint + '.csv'))
    return nationalTimeSeries.iloc[0].tolist()


class COVID19_World:
  '''
  Covid-19 Class for processing data at world granularity
  '''

  def __init__(self):
    '''
    Setup globals at the instance level
    '''
    self.DATAFILES = ['time_series_covid19_confirmed_global.csv', 'time_series_covid19_deaths_global.csv']
    # 'time_series_covid19_testing_global.csv' not available yet

  def extract(self, dataSync):
    '''
    Extracts all time series and collates it by country as well as at the aggregated world-level
    :return: None
    '''

    # run DATAMART setup to ensure most recent data is synced
    if dataSync: CSSE_COVID19.setup()

    # process each timeseries data file at all granularities
    for datafile in self.DATAFILES:
      datapoint = datafile.split('.')[0].split('_')[3]
      filepath = os.path.join(ENVCFG.FILESYSTEM.TIMESERIES_ROOTPATH, datafile)
      dataDf = pd.read_csv(filepath, sep=',', header=0)

      dataDf.drop(['Lat', 'Long'], axis=1, inplace=True)
      dataDf['Province/State'].fillna('', inplace=True)
      dataDf.fillna(value=0, inplace=True)

      countries = dataDf['Country/Region'].unique()
      byCountryDf = pd.DataFrame(columns=countries, index=dataDf.columns[2:])
      byCountryDf.fillna(0, inplace=True)

      for country in countries:
        countryDf = dataDf[dataDf['Country/Region'] == country]

        countryDataExtractor = COVID19_Country(country, countryDf, datapoint)
        nationalTimeSeries = countryDataExtractor.extract()
        byCountryDf[country] = nationalTimeSeries

      byCountryDf = byCountryDf.T
      byCountryDf.index.name = 'Country/Region'
      byCountryDf.to_csv(os.path.join(ENVCFG.FILESYSTEM.DATA_ROOT, 'kq', 'WORLD', 'time_series_' + datapoint + '.csv'))

    # separate calls for state and county data extraction based on new datafiles structure
    for country in ['US']:
      COVID19_Country.extractByState_fromCountryFiles(country)
      COVID19_Country.extractByCounty_fromCountryFiles(country)


if __name__ == '__main__':
  COVID19_World().extract(dataSync=True)
