import json
import os
import pickle
import random

import numpy as np
import pandas as pd
from scipy.stats import truncnorm

from forecasting.utils import map_to_date, split_historic_forecast
from hospital.people import Patient

DIRNAME = os.path.dirname(__file__)


_MAP_SPECIALTIES = {
    "Trauma & Orthopaedic": "trauma_and_orthopaedic",
    "General Internal Medicine": "general",
    "General Surgery": "general",
    "Respiratory Medicine": "respiratory",
    "Endocrinology and Diabetes": "endocrinology",
    "Geriatric Medicine": "elderly_care",
    "Gastroenterology": "gastroenterology",
    "Cardiology": "cardiology",
}


try:
    with open(
        os.path.join(DIRNAME, "../../data/specialty_info.json")
    ) as json_file:
        _SPECIALTY_INFO = json.load(json_file)
except FileNotFoundError as e:
    print("Specialty info not found")
    raise e

try:
    with open(
        os.path.join(DIRNAME, "../../data/hourly_elective_prob.json")
    ) as json_file:
        _HOURLY_ELECTIVE_PROB = json.load(json_file)
except FileNotFoundError as e:
    print("Hourly elective probability not found")
    raise e


class PatientSampler:
    """
    Samples number of patients based on forecast for specific hour
    of day and day of week.

    Attributes
    ----------
    day: str
        Day of the week
    hour: int
        Hour of the day, range 0-23
    historic: bool, default False
        Whether to sample historic patients or generate random ones, default
        is sampling randomly.
    """

    def __init__(self, day: str, hour: int, historic: bool = False):
        self.day = day.lower()
        self.hour = hour
        self.historic = historic
        self.number_of_patients = self.forecast_data()
        self.patient_data = self.historic_data()

    def historic_data(self) -> pd.DataFrame:
        if self.historic:
            return _load_patient_data()

    def forecast_data(self) -> np.ndarray:
        if self.historic:
            return _load_samples_from_file(self.day, self.hour)
        else:
            return np.random.randint(0, high=25, size=168, dtype=int)

    def sample_patients(
        self,
        forecast_window: int,
        num_samples: int,
        filtered: bool = True,
    ) -> list:
        """
        Provides samples of historic patients.

        Parameters
        ----------
        forecast_window: int
            Number of hours ahead to sample patients for
        num_samples: int
            Number of separate samples from posterior of forecast
        filtered: bool, default True
            Whether patients should be filtered to just in scope specialites,
            etc. and whether to change to instances of Patient class

        Returns
        -------
        samples: dict of dicts
            First level keys are int, 0-num_samples, one dict for each sample
            Second level keys are str, 'day-hour' from the chosen day and hour
            iterated to forecast_window hours in the future
        """

        samples = {}

        for n in range(0, num_samples):

            if self.historic:
                # Take random row from posterior and cut to forecast window
                # length
                predicted_numbers = self.number_of_patients[
                    random.randint(0, len(self.number_of_patients) - 1),
                    :forecast_window,
                ]
            else:
                # Take randomly generated patient numbers
                predicted_numbers = self.number_of_patients[:forecast_window]

            patients = {}

            day_names = [
                "monday",
                "tuesday",
                "wednesday",
                "thursday",
                "friday",
                "saturday",
                "sunday",
            ]
            day_nums = list(range(0, 7))
            hour_nums = list(range(0, 24))

            iter_day = day_names.index(self.day)
            iter_hour = hour_nums.index(self.hour)

            for num in predicted_numbers:

                if self.historic:

                    # Find patients who were admitted on correct day and hour
                    match_ind = self.patient_data[
                        (self.patient_data["ADMIT_DAY"] == day_nums[iter_day])
                        & (
                            self.patient_data["ADMIT_HOUR"]
                            == hour_nums[iter_hour]
                        )
                    ].index
                    # Sample patients that match (with replacement) until we
                    # have number specified by the posterior row
                    sample_ind = match_ind[
                        np.random.choice(len(match_ind), num, replace=True)
                    ]
                    # Select sampled patients from patient data
                    patient_sample = self.patient_data.loc[
                        sample_ind, :
                    ].reset_index(drop=True)

                else:

                    # Generate random patients
                    patient_sample = generate_random_patients(
                        num, iter_day, iter_hour
                    ).reset_index(drop=True)

                if filtered:
                    # Filter out patients who are elective, under 18 or from
                    # certain specialties
                    patient_sample = filter_patients(patient_sample)
                    # Fill in synthetic magnets data for patients with none
                    patient_sample = fill_magnets(patient_sample)
                    # Change patient data from pandas dataframe to instances of
                    # Patient class
                    patients[
                        str(day_names[iter_day])
                        + "-"
                        + str(hour_nums[iter_hour])
                    ] = pandas_to_patients(patient_sample)

                else:
                    # Return patient list without changing format to get
                    # percentages of historic patients male/female, etc.
                    patients[
                        str(day_names[iter_day])
                        + "-"
                        + str(hour_nums[iter_hour])
                    ] = patient_sample

                iter_hour += 1
                if iter_hour == 24:
                    iter_day += 1
                    iter_hour = 0
                if iter_day == 7:
                    iter_day = 0

            samples[n] = patients

        return samples


def _load_samples_from_file(day: str, hour: int) -> np.ndarray:
    """
    Reads in full posterior from file and cuts down to that date and 24hrs
    in future.
    """

    date = map_to_date(day, hour)

    try:
        results = pickle.load(
            open(
                os.path.join(DIRNAME, "../../data/forecast_results.pkl"), "rb"
            )
        )
        time = results["time"]
        posterior = results["posterior"]

        # Would only consider patients in next 24hrs for sampling and none in
        # the past
        historic_hours = 0
        forecast_hours = 24
        _, forecast_ids = split_historic_forecast(
            time, date, historic_hours, forecast_hours
        )

        return posterior[:, forecast_ids]

    except FileNotFoundError as e:
        print("Forecast data not found")
        raise e


def _load_patient_data() -> pd.DataFrame:
    """Reads in historic patients."""

    try:
        patient_df = pd.read_csv(
            os.path.join(DIRNAME, "../../data/patient_df.csv"),
            index_col=0,
        )
        return patient_df

    except FileNotFoundError as e:
        print("Patient data CSV not found")
        raise e


def generate_random_patients(
    num_patients: int, day: int, hour: int
) -> pd.DataFrame:
    """Creates random patient dataframe."""

    patient_data = {}
    patient_data["DIM_PATIENT_ID"] = np.random.randint(
        7000000, 8000000, size=num_patients
    )
    patient_data["SEX_DESC"] = np.random.choice(
        ["Male", "Female"], p=[0.50, 0.50], size=num_patients
    )
    patient_data["AGE"] = np.random.randint(0, 100, size=num_patients)
    patient_data["ADMIT_DAY"] = np.array([day] * num_patients)
    patient_data["ADMIT_HOUR"] = np.array([hour] * num_patients)
    patient_data["LOS_HOURS"] = np.random.exponential(
        scale=10, size=num_patients
    )

    # Picks based on probability of elective each hour
    patient_data["ELECTIVE"] = np.random.choice(
        [0, 1],
        p=[
            1 - _HOURLY_ELECTIVE_PROB[str(hour)],
            _HOURLY_ELECTIVE_PROB[str(hour)],
        ],
        size=num_patients,
    )

    # Picks specialty with probability
    patient_data["ADMIT_SPEC"] = np.random.choice(
        [k for k in _SPECIALTY_INFO.keys()],
        p=[v["probability"] for v in _SPECIALTY_INFO.values()],
        size=num_patients,
    )

    # Picks correct division based on specialty
    patient_data["ADMIT_DIV"] = np.empty((num_patients), dtype=object)
    for patient in range(0, num_patients):
        if _SPECIALTY_INFO[patient_data["ADMIT_SPEC"][patient]]["is_medical"]:
            patient_data["ADMIT_DIV"][patient] = "Medicine"
        else:
            patient_data["ADMIT_DIV"][patient] = "Surgery"

    # Leaves as nan to be filled out by fill_magnets function
    patient_data["COVID Positive"] = np.empty((num_patients)) * np.nan
    patient_data["COVID Re-Swab"] = np.empty((num_patients)) * np.nan
    patient_data["Dementia"] = np.empty((num_patients)) * np.nan
    patient_data["End Of Life"] = np.empty((num_patients)) * np.nan
    patient_data["Exposed to COVID"] = np.empty((num_patients)) * np.nan
    patient_data["Falls"] = np.empty((num_patients)) * np.nan
    patient_data["Visual Impairment"] = np.empty((num_patients)) * np.nan
    patient_data["Visual Supervision"] = np.empty((num_patients)) * np.nan

    patient_df = pd.DataFrame.from_dict(patient_data)

    return patient_df


def _map_speciality(specialty: str) -> str:
    """Maps historic patient's specialty to properties in Patient class."""

    try:
        return _MAP_SPECIALTIES[specialty]
    except KeyError:
        print("Incorrect Patient Specialty: {specialty}")


def _map_suspected_covid(swab: int, exposed: int) -> bool:
    """Maps historic patient's COVID status to True or False."""
    if swab == 1 or exposed == 1:
        return True
    else:
        return False


def _map_acute_surgical(department: str, elective: int) -> bool:
    """Maps historic patient's acute surgical status to True or False."""
    if department == "Surgery" and elective == 0:
        return True
    else:
        return False


def _map_mobility(
    dementia: int,
    falls: int,
    visual_impairment: int,
    visual_supervisation: int,
) -> bool:
    """Maps historic patient's mobility status to True or False."""
    if dementia + falls + visual_impairment + visual_supervisation > 0:
        return True
    else:
        return False


def _sample_weight() -> float:
    """Draws weight from truncated normal distribution."""
    my_a = 30
    my_b = 120
    my_mean = 70
    my_std = 12
    a, b = (my_a - my_mean) / my_std, (my_b - my_mean) / my_std

    return round(truncnorm.rvs(a=a, b=b, loc=my_mean, scale=my_std), 2)


def _sample_high_acuity() -> bool:
    """
    Draws EWS score from geometric distribution, uses this to map high acuity
    to True or False.
    """
    theta = 0.5
    EWS_score = np.random.geometric(theta) - 1

    if EWS_score > 5:
        return True
    else:
        return False


def _sample_immunosupressed() -> bool:
    """Returns True with probability of 0.5%."""
    immunosupressed = np.random.choice([0, 1], p=[0.995, 0.005])

    if immunosupressed == 1:
        return True
    else:
        return False


def _sample_infection_control() -> bool:
    """Returns True with probability of 1%."""
    infection_control = np.random.choice([0, 1], p=[0.99, 0.01])

    if infection_control == 1:
        return True
    else:
        return False


def pandas_to_patients(df: pd.DataFrame) -> list:
    """Maps patient attributes from dataframe to Patient class."""

    patients = []

    try:
        for row in df.index:
            patients.append(
                Patient(
                    name=str(df.loc[row, "DIM_PATIENT_ID"]),
                    sex=str(df.loc[row, "SEX_DESC"]),
                    weight=_sample_weight(),
                    department=str(df.loc[row, "ADMIT_DIV"]),
                    age=int(df.loc[row, "AGE"]),
                    specialty=_map_speciality(str(df.loc[row, "ADMIT_SPEC"])),
                    is_known_covid=bool(
                        int(float(df.loc[row, "COVID Positive"]))
                    ),
                    is_suspected_covid=_map_suspected_covid(
                        int(float(df.loc[row, "COVID Re-Swab"])),
                        int(float(df.loc[row, "Exposed to COVID"])),
                    ),
                    is_acute_surgical=_map_acute_surgical(
                        df.loc[row, "ADMIT_DIV"],
                        int(df.loc[row, "ELECTIVE"]),
                    ),
                    is_elective=bool(int(df.loc[row, "ELECTIVE"])),
                    needs_mobility_assistence=_map_mobility(
                        int(float(df.loc[row, "Dementia"])),
                        int(float(df.loc[row, "Falls"])),
                        int(float(df.loc[row, "Visual Impairment"])),
                        int(float(df.loc[row, "Visual Supervision"])),
                    ),
                    is_dementia_risk=bool(int(float(df.loc[row, "Dementia"]))),
                    is_high_acuity=_sample_high_acuity(),
                    is_immunosupressed=_sample_immunosupressed(),
                    is_end_of_life=bool(
                        int(float(df.loc[row, "End Of Life"]))
                    ),
                    is_infection_control=_sample_infection_control(),
                    is_falls_risk=bool(int(float(df.loc[row, "Falls"]))),
                    needs_visual_supervision=bool(
                        int(float(df.loc[row, "Visual Supervision"]))
                    ),
                    expected_length_of_stay=int(df.loc[row, "LOS_HOURS"]),
                    length_of_stay=0,
                )
            )
        return patients

    except KeyError as e:
        print("Not all fields present in patient data")
        raise e


def filter_patients(df: pd.DataFrame) -> pd.DataFrame:
    """
    Removes patients from the sample who are under 18, elective, or in a
    division or specialty not dealt with in the POC.
    """

    df = df[df["AGE"] >= 18]

    df = df[df["ELECTIVE"] == 0]

    spec_keep = [
        "Trauma & Orthopaedic",
        "General Internal Medicine",
        "General Surgery",
        "Respiratory Medicine",
        "Gastroenterology",
        "Endocrinology and Diabetes",
        "Cardiology",
        "Geriatric Medicine",
    ]
    df = df[df["ADMIT_SPEC"].isin(spec_keep)]

    div_keep = ["Surgery", "Medicine"]
    df = df[df["ADMIT_DIV"].isin(div_keep)]

    return df


def fill_magnets(df: pd.DataFrame) -> pd.DataFrame:
    """
    For patients with no magnets data from Patient Flow, fills in the values
    with synthetic data. Probability of any magnet being selected for any
    patient is based on average number of patients with that magnet in the
    data.
    """

    magnets = [
        "COVID Positive",
        "COVID Re-Swab",
        "Dementia",
        "End Of Life",
        "Exposed to COVID",
        "Falls",
        "Visual Impairment",
        "Visual Supervision",
    ]

    # Probabilty of magnet being selected
    probability = [0.004, 0.032, 0.044, 0.025, 0.002, 0.245, 0.01, 0.069]

    for magnet, prob in zip(magnets, probability):

        df.fillna(
            value={magnet: np.random.choice([0, 1], p=[1 - prob, prob])},
            inplace=True,
        )

    # Checks only one COVID magnet selected, if multiple, picks random
    for row in df.index:

        if (
            df.loc[row, "COVID Positive"]
            + df.loc[row, "COVID Re-Swab"]
            + df.loc[row, "Exposed to COVID"]
            > 1
        ):

            df.loc[row, "COVID Positive"] = 0
            df.loc[row, "COVID Re-Swab"] = 0
            df.loc[row, "Exposed to COVID"] = 0
            df.loc[
                row,
                np.random.choice(
                    ["COVID Positive", "COVID Re-Swab", "Exposed to COVID"]
                ),
            ] = 1

    return df
