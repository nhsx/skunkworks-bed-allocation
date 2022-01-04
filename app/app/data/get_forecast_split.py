import os
import pickle

import numpy as np
import pandas as pd

from forecasting.patient_sampler import PatientSampler
from forecasting.utils import map_to_date

import argparse

DIRNAME = os.path.dirname(__file__)


def main(num_samples=1000):
    """
    Generates patients based on forecast and finds the split in attributes,
    e.g. number of male vs female patients
    """

    keys = []
    days = []
    hours = []

    # Goes through each day and hour combination
    for day in [
        "monday",
        "tuesday",
        "wednesday",
        "thursday",
        "friday",
        "saturday",
        "sunday",
    ]:
        for hour in range(0, 24):
            keys.append(day + "-" + str(hour))
            days.append(day)
            hours.append(hour)

    # Want splits to be for any patients admitted in next 4 hours
    hours_ahead = 4

    male = []
    elective = []
    medical = []
    over_18 = []
    over_65 = []

    for i, (key, day, hour) in enumerate(zip(keys, days, hours)):

        # Initialises patient sampler, when dummy data being used set
        # historic=False
        sampler = PatientSampler(day, hour, historic=True)
        # Samples patients according to forecast with filters off as want to
        # proportion of elective, etc. patients rather than filtering
        samples = sampler.sample_patients(
            hours_ahead, num_samples, filtered=False
        )

        male_split = []
        elective_split = []
        medical_split = []
        over_18_split = []
        over_65_split = []
        num_patients = []

        for n in range(0, num_samples):

            # Concatenates lists of patients for next 4 hours
            for t in range(0, hours_ahead):

                if t == 0:

                    patients = samples[n][key]

                else:

                    if (i + t) >= len(keys):

                        patients = pd.concat(
                            [patients, samples[n][keys[i + t - len(keys)]]]
                        )

                    else:

                        patients = pd.concat(
                            [patients, samples[n][keys[i + t]]]
                        )

            num_patients = len(patients)

            # If there are patients, find fraction that are male, elective,
            # medical, over 18 and over 65 and append for this sample
            if num_patients > 0:

                male_split.append(
                    sum(patients["SEX_DESC"] == "Male") / num_patients
                )
                elective_split.append(
                    sum(patients["ELECTIVE"] == 1) / num_patients
                )
                medical_split.append(
                    sum(patients["ADMIT_DIV"] == "Medicine") / num_patients
                )
                over_18_split.append(sum(patients["AGE"] > 18) / num_patients)
                over_65_split.append(sum(patients["AGE"] > 65) / num_patients)

        # Finds average percentage across all samples
        male.append(int(np.mean(male_split) * 100))
        elective.append(int(np.mean(elective_split) * 100))
        medical.append(int(np.mean(medical_split) * 100))
        over_18.append(int(np.mean(over_18_split) * 100))
        over_65.append(int(np.mean(over_65_split) * 100))

    # Saves split to dict
    results_split = {}
    results_split["time"] = pd.date_range(
        map_to_date("monday", 0), periods=168, freq="1H"
    )
    results_split["male"] = np.array(male)
    results_split["elective"] = np.array(elective)
    results_split["medical"] = np.array(medical)
    results_split["over_18"] = np.array(over_18)
    results_split["over_65"] = np.array(over_65)

    pickle.dump(
        results_split,
        open(
            os.path.join(
                DIRNAME,
                "forecast_split_random.pkl",
            ),
            "wb",
        ),
    )


if __name__ == "__main__":

    # Get arguments from command line
    # (If args are not specified default values will be used.)
    parser = argparse.ArgumentParser(
        description="""The purpose of `get_forecast_split.py` is to create the file `forecast_split_random.pkl` containing 
        split of patient demographics based on historic data."""
    )

    # Args to generate
    parser.add_argument(
        "--number_of_samples",
        "-n",
        type=int,
        default=1000,
        help="[int] Number of samples to use from the posterior. Default is 1000.",
    )

    # Read arguments from the command line
    args = parser.parse_args()

    main(args.number_of_samples)
