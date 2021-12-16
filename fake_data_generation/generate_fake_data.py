"""
This file generates 4 fake data files: 2 csv files and 2 json files.
This file generates fake data randomly.
The purpose of this data is to test the running of the models and setup of the repo.
Field values are generated randomly independently of each other.
Instructions on how to run this file can be found in the README.md in this directory.
"""

import os
import argparse
import json
import numpy as np
import pandas as pd
import random

from data_preparation.create_json_files import (
    create_df_prob_json,
    create_specialty_info_json,
)

# Get arguments from command line
# (If args are not specified default values will be used.)
parser = argparse.ArgumentParser(
    description="""The purpose of `generate_fake_data.py` is to create four files: `patient_df.csv`, `historic_admissions.csv`, `hourly_elective_prob.json`, and `specialty_info.json` file with fake data with the following intended applications: 
    An example of how data needs to be formatted to be passed into the model and to test the setup and running of the repo."""
)

# Args to generate
parser.add_argument(
    "--number_of_records",
    "-nr",
    type=int,
    default=100,
    help="[int] Number of fake patient records to generate. Default is 100.",
)

parser.add_argument(
    "--directory_name",
    "-dn",
    default="fake_data_files",
    type=str,
    help="[str] Running this script creates a new directory by this name. Directory will not over write previous directory if directory name already exists.",
)

parser.add_argument(
    "--seed",
    "-s",
    default=None,
    type=int,
    help="[int] If specified will ensure result is reproducible. Default is set to None so will generate a different result each time.",
)

# Read arguments from the command line
args = parser.parse_args()

# Create directory for files to be save to
os.mkdir(args.directory_name)


# Set seed if specified:
if args.seed is not None:
    np.random.seed(seed=args.seed)


# -----CREATE patient_df.csv-------------------------------------------------------
# ----------------------------------------------------------------------------------

# Load data_description.json to get columns required for training data
with open("../config/patient_data_dictionary.json", "r") as file:
    data_dictionary = json.load(file)

# Create dataframe with original data fields
columns = data_dictionary["fields"][0].keys()
df = pd.DataFrame(columns=columns)

# Load data_categories.json to get the data categories required for each field in the fake data
with open(
    "../config/fake_data_categories/patient_fake_data_categories.json", "r"
) as file:
    data_cat = json.load(file)

# Assign data categories to fields in dataframe
for column in columns:
    if column in data_cat.keys():
        df[column] = np.random.choice(
            data_cat[column], size=args.number_of_records
        )

# Remaining fields to fill in so they are not null
df["DIM_PATIENT_ID"] = np.random.randint(
    1000, 4000, size=(args.number_of_records)
)
df["AGE"] = np.random.randint(18, 100, size=(args.number_of_records))
df["LOS_HOURS"] = np.random.randint(1, 1000, size=(args.number_of_records))

# Create random time range for the fake data (one month).
date_ranges = pd.date_range(
    start="1855-01-01 00:00:00", end="1855-02-01 00:00:00", freq="h"
)
df["ADMIT_DTTM"] = np.random.choice(date_ranges, size=args.number_of_records)
df["ADMIT_HOUR"] = df["ADMIT_DTTM"].dt.hour

# ----- OUTPUT patient_df.csv-----
df.to_csv(f"{args.directory_name}/patient_df.csv")

# Message to show script has run
print(
    f"Fake Data Generated! File saved: {args.directory_name}/patient_df.csv with {args.number_of_records} records created. Seed was set to {args.seed}."
)


# -----CREATE historic_admissions.csv-------------------------------------------------------
# ----------------------------------------------------------------------------------

# Count the number of patients per hour
forecast = df["ADMIT_DTTM"].value_counts()

# Set index to datetime type
forecast.index.index = pd.DatetimeIndex(forecast.index)

# Ensure file has every hour in the index even if the total number of patients admitted is 0
# Reset index
forecast = forecast.reindex(date_ranges, fill_value=0).reset_index()

# Rename columns to format needed for csv
forecast.rename(
    {"index": "ADMIT_DTTM", "ADMIT_DTTM": "Total"}, axis=1, inplace=True
)

# Order dates
forecast.sort_values("ADMIT_DTTM", inplace=True)

# ----- OUTPUT historic_admissions.csv-----
forecast.reset_index(drop=True).to_csv(
    f"{args.directory_name}/historic_admissions.csv"
)
# Message to show script has run
print(
    f"Fake Data Generated! File saved: {args.directory_name}/historic_admissions.csv."
)


# -----CREATE hourly_elective_prob.json-------------------------------------------------------
# ----------------------------------------------------------------------------------

create_df_prob_json(
    f"{args.directory_name}/patient_df.csv", args.directory_name
)


# -----CREATE hourly_elective_prob.json-------------------------------------------------------
# ----------------------------------------------------------------------------------

create_specialty_info_json(
    f"{args.directory_name}/patient_df.csv",
    "../config/fake_data_categories/fake_speciality_is_medical_mapping.json",
    args.directory_name,
),
