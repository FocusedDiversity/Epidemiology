from setuptools import setup, find_packages

setup(
  name='epidem',
  version='0.0.dev1',
  packages=find_packages(),
  include_package_data=True,
  url='https://github.com/FocusedDiversity/Epidemiology',
  license='Free for non-commercial use',
  author='Synaptiq, Karotene',
  author_email='peshave.ak@gmail.com',
  description='Epidemiology toolkit under-development',
  install_requires=[
    'numpy>=1.18.0,<1.19.0',
    'scipy>=1.4.0,<1.5.0',
    'pandas>=1.0.0,<1.1.0'
  ],
  keywords=['Epidemiology', 'Disease Spread Models', 'Disease Dashboards'],
  classifiers=[
    'Development Status :: 2 - Pre-Alpha',
    'Intended Audience :: Developers',
    'Intended Audience :: Education',
    'Intended Audience :: Science/Research',
    'Intended Audience :: Healthcare Industry',
    'License :: Free for non-commercial use',
    'Operating System :: MacOS :: MacOS X',
    'Operating System :: Microsoft :: Windows',
    'Operating System :: POSIX',
    'Programming Language :: Python :: 3',
    'Topic :: Scientific/Engineering :: Medical Science Apps.',
    'Topic :: Scientific/Engineering :: Visualization',
    'Topic :: Scientific/Engineering :: Information Analysis',
  ]
)
