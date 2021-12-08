# Generating fake data

## Overview and Purpose
This directory contains two files called 
- `forecast_generate_fake_data.py`
- `patient_generate_fake_data.py`

The purpose of both `forecast_generate_fake_data.py` and `patient_generate_fake_data.py` is to create a `.csv` file with fake data with the following intended applications:
- As an example of how data needs to be formatted to be passed into the models.
- To ensure the files are being generated correctly to test GUI setup.
- To test the setup and running of the repo.

The following should be noted with regards to using the fake data generators and the artefacts produced by using fake data:
- *DO NOT* use the model artefacts (`.pkl` files) generated from the fake data to make predictions which will be used in any real world application.
- *DO NOT* use the fake data generated to inform any insights to be applied to a real world setting.
- *DO NOT* use the fake data to test the performance of the model.

The data is generated completely randomly, with each field having random values generated independently of other fields. This generator was created having never been exposed to the real data.

Note a number of the fields will show only test categories and may not be reflective of the types of categories or number of categories types in each field. However the formatting of the fields is reflective as an example of what is required to run the models.

## `forecast_generate_fake_data.py`
Everything needed to generate fake data using `forecast_generate_fake_data.py` is contained in the file and does not need any additional files to run.

### How to run
Before running ensure your environment is set up as described in: [README.md](README.md) 

Please note all bash commands listed below assume the working directory is `fake_data_generation` (this directory).

There are a number of parameters to run the `patient_generate_fake_data.py`, available using the `--help` flag:

```
$ python forecast_generate_fake_data.py --help
usage: forecast_generate_fake_data.py [-h] [--number_of_records NUMBER_OF_RECORDS] [--filename FILENAME]
                                      [--seed SEED]

The purpose of `forecast_generate_fake_data.py` is to create a `.csv` file with fake data with the following
intended applications: An example of how data needs to be formatted to be passed into the model and to test
the setup and running of the repo.

optional arguments:
  -h, --help            show this help message and exit
  --number_of_records NUMBER_OF_RECORDS, -nr NUMBER_OF_RECORDS
                        [int] Number of records to generate. Default is 100.
  --filename FILENAME, -fn FILENAME
                        [str] The name of the csv file saved at the end (do not add.csv). The default name
                        is set to "forecast_fake_data". This will generate a file called
                        "forecast_fake_data.csv" .
  --seed SEED, -s SEED  [int] If specified will ensure result is reproducible. Default is set to None so
                        will generate a different result each time.
```

To test the setup and the running of the repo it is recommended to run `forecast_generate_fake_data` with the following arguments:
  ```bash
$ python forecast_generate_fake_data.py -nr 200
```
or depending on your machine setup:

  ```bash
$ python3 forecast_generate_fake_data -nr 200
``` 


## `patient_generate_fake_data.py`

The categories for the fields in `patient_generate_fake_data.py` can be found in [patient_fake_data_categories.json](config/fake_data_categories/patient_fake_data_categories.json). The categories specified in this file are randomly chosen to fill the corresponding fields in the fake data. This is done in `patient_generate_fake_data.py`. 

Data fields that do not have their categories specified in [patient_fake_data_categories.json](../config/fake_data_categories/patient_fake_data_categories.json) or are not categorical variables have the fake data required generated in `patient_generate_fake_data.py` line by line to show how the data is being generated for each field. In `patient_generate_fake_data.py` the fields are split into the field data type (e.g. str, int) required for the models to train.


### How to run
Before running ensure your environment is set up as described in: [README.md](README.md) 

Please note all bash commands listed below assume the working directory is `fake_data_generation` (this directory).

There are a number of parameters to run the `patient_generate_fake_data.py`, available using the `--help` flag:

```
$ python patient_generate_fake_data.py --help
usage: patient_generate_fake_data.py [-h] [--number_of_records NUMBER_OF_RECORDS] [--filename FILENAME] [--seed SEED]

The purpose of `patient_generate_fake_data.py` is to create a `.csv` file with fake data with the following
intended applications: An example of how data needs to be formatted to be passed into the model and to test
the setup and running of the repo.

optional arguments:
  -h, --help            show this help message and exit
  --number_of_records NUMBER_OF_RECORDS, -nr NUMBER_OF_RECORDS
                        [int] Number of records to generate. Default is 100.
  --filename FILENAME, -fn FILENAME
                        [str] The name of the csv file saved at the end (do not add.csv). The default name
                        is set to "patient_fake_data". This will generate a file called "patient_fake_data.csv" .
  --seed SEED, -s SEED  [int] If specified will ensure result is reproducible. Default is set to None so
                        will generate a different result each time.
  ```

To test the setup and the running of the repo it is recommended to run `patient_generate_fake_data` with the following arguments:
  ```bash
$ python patient_generate_fake_data.py -nr 200
```
or depending on your machine setup:

  ```bash
$ python3 patient_generate_fake_data.py -nr 200
``` 