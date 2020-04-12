All datasets are accompanied with a sync script snippet (if needed) in the `data/data_sync.sh` shell script. The snippet for the CSSE COVID-19 Dataset is included and is as follows:
```bash
# snippet to sync CSSE COVID-19 Dataset repository
if [ -d COVID-19 ] && [ "$(ls -A COVID-19)" ]
then
  cd COVID-19/
  git pull origin master
  cd ../
else
  git clone https://github.com/CSSEGISandData/COVID-19.git
fi
```
This snippet syncs the dataset from the github repository where the data is updated periodically. All dataset syncs should download/update data inside the `data/[dataset_name]` folder.

All code related to extracting and/or restructuring a dataset resides in the `epidemiology/datamart` package. A new python file is used for every dataset that is included in this codebase. The code to restructure and organize the CSSE COVID-19 timeseries data is in the `datamart/csse_covid19` python file.

As a best practice, any new dataset included in the codebase should be accompanied, if needed, with:
1. Data sync bash snippet in `data/data_sync.sh`
1. Extraction/restructuring code in `datamart/[dataset].py`

[Previous: Setup](./setup.md)\
[Next: Developing Models](./models.md) \
[Back to main index](../README.md) 