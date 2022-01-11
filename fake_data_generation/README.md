# Generating fake data

## Overview and Purpose
This directory contains one file called 
- `generate_fake_data.py`

The purpose of `generate_fake_data.py` is to create four files with fake data in the following order: 

file|description
---|---
`patient_df.csv`| This fake data file will follow the data dictionary as outlined [here.](../config/patient_data_dictionary.json)
`historic_admissions.csv`| This aggreates the number of patients from `patient_df.csv` by date and hour. This fake data file will follow the data dictionary as outlined [here.](../config/historic_admissions_data_dictionary.json)
`hourly_elective_prob.json`| More information about this file can be found [here.](../src/data_preparation/README.md)
`specialty_info.json`| More information about this file can be found [here.](../src/data_preparation/README.md)

The fake data is intended for us with the following applications:
- As an example of how data needs to be formatted to be passed into the models.
- To ensure the files are being generated correctly to test GUI setup.
- To test the setup and running of the repo.

The following should be noted with regards to using the fake data generators and the artefacts produced by using fake data:
- *DO NOT* use the model artefacts (`.pkl` files) generated from the fake data to make predictions which will be used in any real world application.
- *DO NOT* use the fake data generated to inform any insights to be applied to a real world setting.
- *DO NOT* use the fake data to test the performance of the model.

The data is generated completely randomly, with each field having random values generated independently of other fields. The ward specialties used are real, and have not been switched to fake names due to hard coding within the codebase. All other fields were created having never been exposed to the real data.

Note a number of the fields will show only test categories and may not be reflective of the types of categories or number of categories types in each field. However the formatting of the fields is reflective as an example of what is required to run the models.


## `generate_fake_data.py`

The categories for the fields in `generate_fake_data.py` can be found in [patient_fake_data_categories.json](config/fake_data_categories/patient_fake_data_categories.json). The categories specified in this file are randomly chosen to fill the corresponding fields in the fake data. This is done in `generate_fake_data.py`. 

Data fields that do not have their categories specified in [patient_fake_data_categories.json](../config/fake_data_categories/patient_fake_data_categories.json) or are not categorical variables have the fake data required generated in `generate_fake_data.py` line by line to show how the data is being generated for each field. In `generate_fake_data.py` the fields are split into the field data type (e.g. str, int) required for the models to train.

The fake data generator creates a new directory in the directory the script is ran, the four files described above are then stored in the new directory. An example layout after `generate_fake_data.py` has run with the default new directory name (`fake_data_files`) can be seen below:
```
Folder
│   generate_fake_data.py
|
└───fake_data_files
    │   patient_df.csv
    │   historic_admissions.csv
    |   hourly_elective_prob.json
    |   specialty_info.json
```


### How to run
Before running ensure your environment is set up in development mode as described in: [README.md](../README.md#Getting-Started).

Please note all bash commands listed below assume the working directory is `fake_data_generation` (this directory).

*Note:*
- The fake data generator will generate fake data between dates `1855-01-01 00:00:00`. and `1855-06-01 00:00:00` at 1 hour intervals. (`../src/forecasting/utils.py` has been updated for this to run.)
- `generate_fake_data.py` creates a new directory each time it runs. If the directory name already exists an error will be thrown

There are a number of parameters to run the `generate_fake_data.py`, available using the `--help` flag:

```
$ python generate_fake_data.py --help
usage: generate_fake_data.py [-h] [--number_of_records NUMBER_OF_RECORDS]
                                     [--directory_name DIRECTORY_NAME] [--seed SEED]

The purpose of `generate_fake_data.py` is to create four files: "patient_df.csv", "historic_admissions.csv", "hourly_elective_prob.json", and "specialty_info.json" file with fake data with the following intended applications: An example of how data needs to be formatted to be passed into the model and to test the setup and running of the repo.

optional arguments:
  -h, --help            show this help message and exit
  --number_of_records NUMBER_OF_RECORDS, -nr NUMBER_OF_RECORDS
                        [int] Number of fake patient records to generate. Default is 100.
  --directory_name DIRECTORY_NAME, -dn DIRECTORY_NAME
                        [str] Running this script creates a new directory by this name. Directory will not over write previous directory if directory name already exists. Default name is "fake_data_files".
  --seed SEED, -s SEED  [int] If specified will ensure result is reproducible. Default is set to None so will generate a different result each time.
  ```

To test the setup and the running of the repo it is recommended to run `generate_fake_data` with the following arguments:
  ```bash
$ python generate_fake_data.py -nr 2000
```
or depending on your machine setup:

  ```bash
$ python3 generate_fake_data.py -nr 2000
```

Once created, copy the contents of `fake_data_files` into the `data/` folder in the root of the repository.