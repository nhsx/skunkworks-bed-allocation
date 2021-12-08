"""
This file generates a fake patient file.
This file generates fake data randomly.
The purpose of this data is to test the running of the models and setup of the repo.
Field values are generated randomly independently of each other.
Instructions on how to run this file can be found in the README.md in this directory.
"""

import argparse
import json
import numpy as np
import pandas as pd
import random

# Get arguments from command line
# (If args are not specified default values will be used.)
parser = argparse.ArgumentParser(
    description="""The purpose of `patient_generate_fake_data.py` is to create a `.csv` file with fake data with the following intended applications: 
    An example of how data needs to be formatted to be passed into the model and to test the setup and running of the repo."""
)

# Args to generate
parser.add_argument(
    "--number_of_records",
    "-nr",
    type=int,
    default=100,
    help="[int] Number of records to generate. Default is 100.",
)
parser.add_argument(
    "--filename",
    "-fn",
    type=str,
    default="patient_fake_data",
    help="""[str] The name of the csv file saved at the end (do not add.csv).
    The default name is set to "patient_fake_data". This will generate a file called "patient_fake_data.csv" . """,
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

# Set seed if specified:
if args.seed is not None:
    np.random.seed(seed=args.seed)

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

# Random time
df["ADMIT_DTTM"] = pd.Timestamp(year=1855, month=1, day=1, hour=12)


# Write dataframe to csv
df.to_csv(f"{args.filename}.csv")

# Message to show script has run
print(
    f"Fake Data Generated! File saved: {args.filename}.csv with {args.number_of_records} records created. Seed was set to {args.seed}."
)
