import io, os
import pandas as pd
import numpy as np
from epidemiology.config import env_config as ENVCFG


def prepDir(dirpath):
  try:
    os.makedirs(dirpath)
  except Exception as ex:
    pass


class DATAMART:
  @classmethod
  def setup(cls):
    '''
    Setup data folders for all countries in the dataset
    :return: None
    '''

    # sync all datasets from their respective repos using data folder shell script
    os.system(' && '.join(['cd ' + ENVCFG.FILESYSTEM.DATA_ROOT,
                           'bash data_sync.sh'
                           ]))

    # retrieve list of countries from on of the data files
    filepath = os.path.join(
      ENVCFG.FILESYSTEM.DATA_ROOT,
      'COVID-19', 'csse_covid_19_data', 'csse_covid_19_time_series', 'time_series_19-covid-Confirmed.csv'
    )
    dataDf = pd.read_csv(filepath, sep=',', header=0)
    countries = dataDf['Country/Region'].unique()

    # create data folders for all countries and for the aggregated world level data
    for country in countries:
      prepDir(os.path.join(ENVCFG.FILESYSTEM.DATA_ROOT, 'kq', country, 'national'))

    prepDir(os.path.join(ENVCFG.FILESYSTEM.DATA_ROOT, 'kq', 'WORLD'))


class COVID_19_CountryExtractor:
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
    else:  # state and/or county level data present
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


class COVID_19_WORLD:
  '''
  Covid-19 Class for processing data at world granularity
  '''

  # path where time series data resides
  ROOTPATH = os.path.join(
    ENVCFG.FILESYSTEM.DATA_ROOT,
    'COVID-19', 'csse_covid_19_data', 'csse_covid_19_time_series'
  )

  def __init__(self):
    '''
    Setup globals at the instance level
    '''
    self.ROOTPATH = self.__class__.ROOTPATH
    self.DATAFILES = ['time_series_19-covid-Confirmed.csv', 'time_series_19-covid-Deaths.csv',
                      'time_series_19-covid-Recovered.csv']

  def extract(self):
    '''
    Extracts all time series and collates it by country as well as at the aggregated world-level
    :return: None
    '''

    # run DATAMART setup to ensure most recent data is synced
    DATAMART.setup()

    # process each timeseries data file at all granularities
    for datafile in self.DATAFILES:
      datapoint = datafile.split('.')[0].split('-')[-1]
      filepath = os.path.join(self.ROOTPATH, datafile)
      dataDf = pd.read_csv(filepath, sep=',', header=0)

      dataDf.drop(['Lat', 'Long'], axis=1, inplace=True)
      countries = dataDf['Country/Region'].unique()
      byCountryDf = pd.DataFrame(columns=countries, index=dataDf.columns[2:])
      byCountryDf.fillna(0, inplace=True)

      for country in countries:
        countryDf = dataDf[dataDf['Country/Region'] == country]

        countryDataExtractor = COVID_19_CountryExtractor(country, countryDf, datapoint)
        nationalTimeSeries = countryDataExtractor.extract()
        byCountryDf[country] = nationalTimeSeries

      byCountryDf = byCountryDf.T
      byCountryDf.index.name = 'Country/Region'
      byCountryDf.to_csv(os.path.join(ENVCFG.FILESYSTEM.DATA_ROOT, 'kq', 'WORLD', 'time_series_' + datapoint + '.csv'))


if __name__ == '__main__':
  COVID_19_WORLD().extract()
