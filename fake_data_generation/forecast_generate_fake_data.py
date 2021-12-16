"""
This file generates a fake forecast file.
This file generates fake data randomly.
The purpose of this data is to test the running of the models and setup of the repo.
Field values are generated randomly independently of each other.
Instructions on how to run this file can be found in the README.md in this directory.
"""

import argparse
import numpy as np
import pandas as pd
import random

# Get arguments from command line
# (If args are not specified default values will be used.)
parser = argparse.ArgumentParser(
    description="""The purpose of `forecast_generate_fake_data.py` is to create a `.csv` file with fake data with the following intended applications: 
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
    default="historic_admissions",
    help="""[str] The name of the csv file saved at the end (do not add.csv).
    The default name is set to "historic_admissions". This will generate a file called "historic_admissions.csv" . """,
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

# Create dataframe with original data fields
df = pd.DataFrame(columns=["ADMIT_DTTM", "Total"])

# Remaining fields to fill in so they are not null
df["ADMIT_DTTM"] = pd.date_range(
    start=pd.Timestamp(year=1850, month=1, day=1, hour=12),
    end=pd.Timestamp(year=1899, month=1, day=1, hour=12),
    periods=args.number_of_records,
)

df["Total"] = np.random.randint(30, 60, size=(args.number_of_records))


# Write dataframe to csv
df.to_csv(f"{args.filename}.csv")

# Message to show script has run
print(
    f"Fake Data Generated! File saved: {args.filename}.csv with {args.number_of_records} records created. Seed was set to {args.seed}."
)
