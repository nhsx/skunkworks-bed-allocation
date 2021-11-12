import os
from typing import Any, Dict, List, Tuple, Union

import cloudpickle
import numpy as np
import pandas as pd
import plotly.graph_objects as go

from agent.policy import greedy_suggestions, populate_hospital
from forecasting.patient_sampler import (
    fill_magnets,
    filter_patients,
    generate_random_patients,
    pandas_to_patients,
)
from hospital.building.building import Hospital
from hospital.building.room import BedBay, SideRoom
from hospital.building.ward import Ward
from hospital.people import Patient, patient_to_dict

DIRNAME = os.path.dirname(__file__)

try:
    WARDS = pd.read_csv(os.path.join(DIRNAME, "data/wards.csv"), index_col=0)
except FileNotFoundError as e:
    print("Ward file not found")
    raise e

FIELD_MAP = {
    "name": "Name",
    "sex": "Sex",
    "department": "Division",
    "specialty": "Specialty",
    "weight": "Weight",
    "age": "Age",
    "is_elective": "Elective",
    "needs_mobility_assistence": "Mobility assistance",
    "is_dementia_risk": "Confused or wandering",
    "is_immunosupressed": "Immunosupressed",
    "is_end_of_life": "End of Life Pathway",
    "is_infection_control": "Infection control (non-COVID)",
    "is_falls_risk": "Falls risk",
    "needs_visual_supervision": "Visual Supervision",
    "is_high_acuity": "High Acuity",
}

BOOL_MAP = {True: "Yes", False: "No", "1": "Yes", "0": "No"}

RESTRICTIONS_MAP = {
    "NoKnownCovid": "Patient COVID-19 positive",
    "NoNonCovid": "Patient COVID-19 negative",
    "NoSuspectedCovid": "Patient COVID-19 suspected",
    "NoPatientsOver100kg": "Patient over 100Kg",
    "NoMobilityAssistance": "Patient not independently mobile",
    "NoDementiaRisk": "Patient confused or wandering.",
    "NoMedical": "Medical patient in surgical ward.",
    "NoSurgical": "Surgical patient in medical ward",
    "IncorrectSex": "Patient and ward sex don't match",
    "NoMixedSex": "Mixed sex bed bay",
    "IncorrectSpecialty": "Patient and ward specialty don't match",
    "NoAcuteSurgical": "Acute surgical patient in Barnwell",
    "ProhibitedSideRoom": "Falls risk patient in side room",
    "NeedsSideRoom": "Patient needs side room",
}
WARNINGS = {
    "IncorrectSex": (
        " - Consider alternative recommendation escalation measures"
    ),
    "NoSurgical": (
        " - Consider upcoming surgery discharges or escalation measures"
    ),
    "NoMedical": (
        " - Consider upcoming medicine discharges or escalation measures"
    ),
    "NoMixedSex": (" - Consider alternative recommendation or bay flipping"),
    "NoKnownCovid": (
        " - Consider alternative recommendation escalation measures"
    ),
    "NoNonCovid": (
        " - Consider alternative recommendation escalation measures"
    ),
    "NoSuspectCovid": (
        " - Consider alternative recommendation escalation measures"
    ),
}


def get_greedy_allocations(
    hospital: Hospital, patient_details: Dict[str, Any]
) -> Tuple[dict, dict]:
    """
    Returns the top 5 greedy allocation suggestions for a patient, providing
    details of each allocations suggestion including ward, room details and
    associated penatly, violated restrictions, user warnings etc.
    """
    patient = _patient_from_dict(patient_details)
    suggestions = greedy_suggestions(hospital, patient, num_beds=5)

    for bed_name in suggestions.keys():
        bed = hospital.find_bed(bed_name)
        ward = bed.room.ward
        bed_details = {
            "Ward Name": ward.name,
            "Ward Specialty": [
                s.name.replace("_", " ") for s in ward.specialty
            ],
            "Room Type": "Side Room"
            if isinstance(bed.room, SideRoom)
            else "Bed Bay",
            "Bed": bed_name,
            "Ward Sex": "Mixed"
            if ward.sex.name == "unknown"
            else ward.sex.name.title(),
            "COVID-19 Status": _ward_covid_status(ward),
            "Availability": len(ward.empty_beds),
            "Number Broken": len(
                suggestions[bed_name]["violated_restrictions"]
            ),
            "Penalty Status": _map_penalties(suggestions[bed_name]["penalty"]),
            "Clean Restrictions": _map_restrictions(
                suggestions[bed_name]["violated_restrictions"]
            ),
        }
        suggestions[bed_name].update(bed_details)
    return pd.DataFrame(suggestions).T.reset_index(drop=True)


def _ward_covid_status(ward: Ward) -> str:
    """Map from Ward restrictions to COVID-19 status."""
    restrictions = [r.__class__.__name__ for r in ward.restrictions]
    if "NoKnownCovid" in restrictions and "NoSuspectedCovid" in restrictions:
        return "Green"
    elif "NoKnownCovid" in restrictions:
        return "Amber"
    elif "NoNonCovid" in restrictions:
        return "Red"


def _map_penalties(penalty: int) -> str:
    """Map from total penalty values to Penalty rating."""
    if penalty >= 10:
        return "High"
    elif penalty >= 3:
        return "Medium"
    else:
        return "Low"


def _map_restrictions(restrictions: list) -> dict:
    """
    Map restrictions class names to display strings and create user warnings
    if applicable.
    """
    _new_restrictions = [
        RESTRICTIONS_MAP.get(r, "") + WARNINGS.get(r, "") for r in restrictions
    ]
    return _new_restrictions


def get_hospital() -> Hospital:
    """
    Loads hospital.
    """

    try:
        with open(os.path.join(DIRNAME, "../../data/hospital.pkl"), "rb") as f:
            hospital = cloudpickle.load(f)
        return hospital
    except FileNotFoundError:
        raise FileNotFoundError("Hospital file not found.")


def get_room_type(room: Union[BedBay, SideRoom]) -> str:
    """Return string representing the type of room."""
    if isinstance(room, BedBay):
        return "Bed Bay"
    elif isinstance(room, SideRoom):
        return "Side Room"
    else:
        return ""


def map_assesment_unit(patient_details: dict) -> str:
    """Return string representing the Assessment unit for a patient."""
    if patient_details["Division"] == "surgical":
        return "MAU"
    elif patient_details["Covid-19 Status"] == "Red":
        return "Clifford"
    else:
        return "DASU"


def get_patient() -> Dict[str, Any]:
    """
    Generate random patient.
    """

    patient = []

    # Check patient generates isn't filtered out
    while len(patient) == 0:

        # Generate 1 random patient for random day and hour
        patient_sample = generate_random_patients(
            1,
            np.random.choice([day for day in range(0, 7)]),
            np.random.choice([hour for hour in range(0, 24)]),
        )
        # Filter patient to check they are in POC specialty, above 18 and not
        # elective
        patient_sample = filter_patients(patient_sample)
        # Fill in synthetic magnets data
        patient_sample = fill_magnets(patient_sample)
        # Change patient data from pandas dataframe to instance of
        # Patient class
        patient = pandas_to_patients(patient_sample)

    # convert to dict
    patient_details = patient_to_dict(patient[0])
    # remove redundant fields
    patient_details.pop("expected_length_of_stay", None)
    patient_details.pop("length_of_stay", None)
    patient_details.pop("is_acute_surgical", None)
    patient_details.pop("bed", None)
    patient_details.pop("restrictions", None)
    # convert covid status
    patient_details = _covid_status(patient_details)
    # tidy field names
    patient_details = {
        (
            FIELD_MAP[field]
            if field in list(FIELD_MAP.keys())
            else field.title()
        ): value
        for field, value in patient_details.items()
    }
    # map booleans
    patient_details = {
        field: (BOOL_MAP[value] if isinstance(value, bool) else value)
        for field, value in patient_details.items()
    }
    # tidy up name
    patient_details["Name"] = np.random.choice(
        ["Alexis Green", "Taylor Brown", "Sam Black", "Morgan Grey"]
    )
    return patient_details, patient


def _covid_status(patient_details: dict) -> dict:
    """
    Map COVID status from Patient class to UI.
    """
    if patient_details["is_known_covid"]:
        patient_details["COVID-19 status"] = "Red"
    elif patient_details["is_suspected_covid"]:
        patient_details["COVID-19 status"] = "Amber"
    else:
        patient_details["COVID-19 status"] = "Green"
    patient_details.pop("is_known_covid", None)
    patient_details.pop("is_suspected_covid", None)
    return patient_details


def _patient_from_dict(patient_details: dict) -> Patient:

    inv_fields = {v: k for k, v in FIELD_MAP.items()}
    class_dict = {}
    for k, v in inv_fields.items():
        if patient_details[k] == "No":
            class_dict[v] = False
        elif patient_details[k] == "Yes":
            class_dict[v] = True
        else:
            class_dict[v] = patient_details[k]

    # inverse map covid status
    if patient_details["Covid-19 Status"] == "Red":
        class_dict.update({"is_known_covid": True})
    elif patient_details["Covid-19 Status"] == "Amber":
        class_dict.update({"is_suspected_covid": True})

    return Patient(**class_dict)


def get_populated_hospital(occupancy: float) -> Hospital:
    """
    Creates a hospital object, patients and returns a populated hospital
    """
    hospital = get_hospital()
    populate_hospital(hospital, occupancy)
    return hospital


def calc_occupancy(ward: Ward) -> int:
    """
    Calculates the occupancy of a ward within the hospital
    """
    # return int((len(ward.patients) / len(ward.beds)) * 100)
    return {"occupied": len(ward.patients), "total": len(ward.beds)}


def get_forecast(day: str, time: int) -> List[np.ndarray]:
    """Dummy function to get forecast"""
    before = np.linspace(2 * np.pi * -7, 0, 7 * 24)
    after = np.linspace(0, 2 * np.pi * 3, 3 * 24)
    n_patients_before = np.sin(before) + np.random.uniform(1, 0.3, 7 * 24)
    n_patients_after = np.sin(after) + np.random.uniform(1, 0.3, 3 * 24)
    forecast_json = {
        "historic": {
            "time": before.tolist(),
            "n_patients": n_patients_before.tolist(),
        },
        "forecast": {
            "time": after.tolist(),
            "n_patients": n_patients_after.tolist(),
        },
    }
    return forecast_json


def make_forecast_figure(forecast: Dict[str, Any]) -> go.Figure:
    """
    Creates the figure showing the forecasted number of patients
    """
    data = [
        go.Scatter(
            x=forecast[period]["time"],
            y=forecast[period]["n_patients"],
            mode="lines+markers",
            marker={"size": 8},
            name=period,
        )
        for period in ["historic", "forecast"]
    ]
    layout = {
        "xaxis": {"title": "time"},
        "yaxis": {"title": "Number of patients"},
        "legend": {"yanchor": "top", "y": 0.99, "xanchor": "left", "x": 0.01},
        "margin": {"t": 20, "b": 10, "l": 20, "r": 20},
        "height": 250,
    }

    return go.Figure(data=data, layout=layout)
