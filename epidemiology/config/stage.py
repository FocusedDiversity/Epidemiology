import os
import pathlib


class FILESYSTEM:
  REPO_ROOT = pathlib.Path(__file__).parent.parent.parent.absolute()
  SRC_ROOT = os.path.join(REPO_ROOT, 'epidemiology')
  DATA_ROOT = os.path.join(REPO_ROOT, 'data')
  TIMESERIES_ROOTPATH = os.path.join(DATA_ROOT, 'COVID-19', 'csse_covid_19_data', 'csse_covid_19_time_series')
