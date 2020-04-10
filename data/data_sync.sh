#!/usr/bin/env bash

# snippet to sync CSSE COVID-19 Dataset repository
if [ -d COVID-19 ] && [ "$(ls -A COVID-19)" ]
then
  cd COVID-19/
  git pull origin master
  cd ../
else
  git clone https://github.com/CSSEGISandData/COVID-19.git
fi