"""
Test suite for forecasting module.
"""
import pandas as pd

from forecasting import pandas_to_patients
from hospital.people import Patient

PATIENT_LIST = [
    Patient(
        name="John",
        sex="male",
        weight=70,
        department="surgery",
        age=37,
        specialty="trauma_and_orthopaedic",
        is_known_covid=False,
        is_suspected_covid=False,
        is_acute_surgical=True,
        is_elective=False,
        needs_mobility_assistence=False,
        is_dementia_risk=False,
        is_high_acuity=True,
        is_immunosupressed=False,
        is_end_of_life=False,
        is_infection_control=False,
        is_falls_risk=False,
        needs_visual_supervision=False,
        expected_length_of_stay=37,
        length_of_stay=0,
    ),
    Patient(
        name="Sarah",
        sex="female",
        weight=70,
        department="medicine",
        age=76,
        specialty="cardiology",
        is_known_covid=True,
        is_suspected_covid=False,
        is_acute_surgical=False,
        is_elective=True,
        needs_mobility_assistence=True,
        is_dementia_risk=True,
        is_high_acuity=True,
        is_immunosupressed=False,
        is_end_of_life=False,
        is_infection_control=False,
        is_falls_risk=True,
        needs_visual_supervision=False,
        expected_length_of_stay=59,
        length_of_stay=0,
    ),
]

PATIENT_JSON = {
    "0": {
        "DIM_PATIENT_ID": "John",
        "SEX_DESC": "Male",
        "AGE": "37",
        "1-2-1": "0.0",
        "COVID Positive": "0.0",
        "COVID Re-Swab": "0.0",
        "Dementia": "0.0",
        "End Of Life": "0.0",
        "Exposed to COVID": "0.0",
        "Falls": "0.0",
        "Learning Disabilities": "1.0",
        "MH High Risk": "0.0",
        "Visual Impairment": "0.0",
        "Visual Supervision": "0.0",
        "ELECTIVE": "0",
        "ADMIT_DIV": "Surgery",
        "ADMIT_SPEC": "Trauma & Orthopaedic",
        "LOS_HOURS": "37",
    },
    "1": {
        "DIM_PATIENT_ID": "Sarah",
        "SEX_DESC": "Female",
        "AGE": "76",
        "1-2-1": "0.0",
        "COVID Positive": "1.0",
        "COVID Re-Swab": "0.0",
        "Dementia": "1.0",
        "End Of Life": "0.0",
        "Exposed to COVID": "0.0",
        "Falls": "1.0",
        "Learning Disabilities": "0.0",
        "MH High Risk": "0.0",
        "Visual Impairment": "0.0",
        "Visual Supervision": "0.0",
        "ELECTIVE": "1",
        "ADMIT_DIV": "Medicine",
        "ADMIT_SPEC": "Cardiology",
        "LOS_HOURS": "59",
    },
}


def test_pandas_to_patients():

    patient_df = pd.DataFrame(PATIENT_JSON).T

    patients = pandas_to_patients(patient_df)

    assert len(patients) == len(PATIENT_LIST)
    assert isinstance(patients[0].weight, float)
    assert isinstance(patients[0].is_high_acuity, bool)
    assert isinstance(patients[0].is_immunosupressed, bool)
    assert isinstance(patients[0].is_infection_control, bool)

    for p_returned, p_validation in zip(patients, PATIENT_LIST):
        # Sampled from a distribution so resetting for tests
        p_returned.weight = p_validation.weight
        p_returned.is_high_acuity = p_validation.is_high_acuity
        p_returned.is_immunosupressed = p_validation.is_immunosupressed
        p_returned.is_infection_control = p_validation.is_infection_control
        # patient restrictions are set dynamically based on above values
        p_returned.restrictions = p_validation.restrictions
        assert p_returned == p_validation
