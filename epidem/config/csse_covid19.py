import os
import pathlib
from . import package as PACKAGE_CFG


class FILESYSTEM:
  TIMESERIES_ROOTPATH = os.path.join(PACKAGE_CFG.FILESYSTEM.DATA_ROOT, 'COVID-19', 'csse_covid_19_data',
                                     'csse_covid_19_time_series')
  TIMESERIES_EXTRACTPATH = os.path.join(PACKAGE_CFG.FILESYSTEM.DATA_ROOT, 'COVID-19-extracted')
