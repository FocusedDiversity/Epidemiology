import os
import pathlib


class FILESYSTEM:
  PACKAGE_ROOT = pathlib.Path(__file__).parent.parent.parent.absolute()
  REPO_ROOT = str(pathlib.Path(__file__).parent.absolute()).split('.venv')[0].split('epidem/')[0]
  SRC_ROOT = os.path.join(PACKAGE_ROOT, 'epidem')
  DATA_ROOT = os.path.join(REPO_ROOT, 'data')
