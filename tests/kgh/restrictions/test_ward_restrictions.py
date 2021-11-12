"""
Test suite for the `hospital.restrictions` module.
"""
import pytest

from hospital.building import SideRoom
from hospital.data import Sex, Specialty
from hospital.equipment.bed import Bed
from hospital.people import Patient
from hospital.restrictions import ward as R


def test_incorrect_sex(hospital):
    hospital.wards[0].sex = Sex.male
    hospital.wards[0].restrictions = [
        R.IncorrectSex(100),
    ]

    patient_male = Patient(
        name="male", sex="male", weight=80.0, department="medicine"
    )
    hospital.admit(patient_male, hospital.beds[0].name)
    assert patient_male in hospital.patients
    assert hospital.wards[0].sex.name == "male"
    assert hospital.eval_restrictions()["score"] == 0
    hospital.clear()

    patient_female = Patient(
        name="female", sex="female", weight=80.0, department="medicine"
    )
    hospital.admit(patient_female, hospital.beds[0].name)
    assert patient_female in hospital.patients
    assert hospital.eval_restrictions()["score"] == 100


def test_no_acute_surgical(hospital):
    hospital.wards[0].restrictions = [R.NoAcuteSurgical(100)]

    patient = Patient(
        name="p1",
        sex="female",
        weight=70.0,
        department="surgery",
        is_acute_surgical=True,
    )

    hospital.admit(patient, hospital.beds[0].name)
    assert patient in hospital.patients
    assert hospital.eval_restrictions()["score"] == 100


@pytest.mark.parametrize(
    "patient, expected_eval",
    [
        (
            Patient(
                "negative",
                sex="male",
                weight=70,
                department="medicine",
                is_known_covid=False,
                is_suspected_covid=False,
            ),
            0,
        ),
        (
            Patient(
                "positive",
                sex="male",
                weight=70,
                department="medicine",
                is_known_covid=True,
                is_suspected_covid=False,
            ),
            100,
        ),
        (
            Patient(
                "suspected",
                sex="male",
                weight=70,
                department="medicine",
                is_known_covid=False,
                is_suspected_covid=True,
            ),
            80,
        ),
        # checking but a patient shouldn't be positive for both covid flags
        (
            Patient(
                "edge",
                sex="male",
                weight=70,
                department="medicine",
                is_known_covid=True,
                is_suspected_covid=True,
            ),
            180,
        ),
    ],
)
def test_covid_green_ward(hospital, patient, expected_eval):
    hospital.wards[0].restrictions = [
        R.NoKnownCovid(100),
        R.NoSuspectedCovid(80),
    ]

    hospital.admit(patient, hospital.beds[0].name)
    assert patient in hospital.patients
    assert hospital.eval_restrictions()["score"] == expected_eval
    hospital.clear()


@pytest.mark.parametrize(
    "patient, expected_eval",
    [
        (
            Patient(
                "negative",
                sex="male",
                weight=70,
                department="medicine",
                is_known_covid=False,
                is_suspected_covid=False,
            ),
            100,
        ),
        (
            Patient(
                "positive",
                sex="male",
                weight=70,
                department="medicine",
                is_known_covid=True,
                is_suspected_covid=False,
            ),
            100,
        ),
        (
            Patient(
                "suspected",
                sex="male",
                weight=70,
                department="medicine",
                is_known_covid=False,
                is_suspected_covid=True,
            ),
            0,
        ),
        # checking but a patient shouldn't be positive for both covid flags
        (
            Patient(
                "edge",
                sex="male",
                weight=70,
                department="medicine",
                is_known_covid=True,
                is_suspected_covid=True,
            ),
            100,
        ),
    ],
)
def test_covid_amber_ward(hospital, patient, expected_eval):
    hospital.wards[0].restrictions = [
        R.NoNonCovid(100),
        R.NoKnownCovid(100),
    ]
    hospital.admit(patient, hospital.beds[0].name)
    assert patient in hospital.patients
    assert hospital.eval_restrictions()["score"] == expected_eval
    hospital.clear()


@pytest.mark.parametrize(
    "patient, expected_eval",
    [
        (
            Patient(
                "negative",
                sex="male",
                weight=70,
                department="medicine",
                is_known_covid=False,
                is_suspected_covid=False,
            ),
            100,
        ),
        (
            Patient(
                "positive",
                sex="male",
                weight=70,
                department="medicine",
                is_known_covid=True,
                is_suspected_covid=False,
            ),
            0,
        ),
        (
            Patient(
                "suspected",
                sex="male",
                weight=70,
                department="medicine",
                is_known_covid=False,
                is_suspected_covid=True,
            ),
            50,
        ),
        # checking but a patient shouldn't be positive for both covid flags
        (
            Patient(
                "edge",
                sex="male",
                weight=70,
                department="medicine",
                is_known_covid=True,
                is_suspected_covid=True,
            ),
            50,
        ),
    ],
)
def test_covid_red_ward(hospital, patient, expected_eval):
    hospital.wards[0].restrictions = [
        R.NoNonCovid(100),
        R.NoSuspectedCovid(50),
    ]
    hospital.admit(patient, hospital.beds[0].name)
    assert patient in hospital.patients
    assert hospital.eval_restrictions()["score"] == expected_eval
    hospital.clear()


@pytest.mark.parametrize(
    "patient",
    [
        Patient(
            name="red",
            sex="female",
            weight=60.0,
            department="medicine",
            is_known_covid=True,
        ),
        Patient(
            name="amber",
            sex="female",
            weight=60.0,
            department="medicine",
            is_suspected_covid=True,
        ),
    ],
)
def test_covid_red_amber_siderooms(hospital, patient):
    """
    Test to check that Red/Amber patients can be
    admitted to siderooms on Green Wards.
    """
    hospital.wards[0].restrictions = [
        R.NoKnownCovid(100),
        R.NoSuspectedCovid(80),
    ]
    sideroom = SideRoom(
        name="sideroom",
        ward=hospital.wards[0],
        beds=[
            Bed(
                name="sideroom_bed",
            )
        ],
    )
    assert sideroom in hospital.rooms

    hospital.admit(patient, "sideroom_bed")
    assert patient in hospital.patients
    assert hospital.eval_restrictions()["score"] == 0
    hospital.clear()


def test_covid_green_siderooms(hospital):
    """
    Test to check that Green patients can be
    admitted to siderooms on Red wards.
    """
    hospital.wards[0].restrictions = [
        R.NoNonCovid(100),
    ]
    sideroom = SideRoom(
        name="sideroom",
        ward=hospital.wards[0],
        beds=[
            Bed(
                name="sideroom_bed",
            )
        ],
    )
    assert sideroom in hospital.rooms

    patient = Patient(
        name="green",
        sex="female",
        weight=60.0,
        department="medicine",
    )

    hospital.admit(patient, "sideroom_bed")
    assert patient in hospital.patients
    assert hospital.eval_restrictions()["score"] == 0
    hospital.clear()


def test_no_patients_over_100kg(hospital):
    hospital.wards[0].restrictions = [R.NoPatientsOver100kg(50)]

    patient_default = Patient("p0", sex="female", department="surgery")
    assert patient_default.weight == 70.0
    hospital.admit(patient_default, hospital.beds[0].name)
    assert patient_default in hospital.patients
    assert hospital.eval_restrictions()["score"] == 0
    hospital.clear()

    patient_heavy = Patient(
        "heavy", sex="female", department="surgery", weight=120.0
    )
    hospital.admit(patient_heavy, hospital.beds[0].name)
    assert patient_heavy in hospital.patients
    assert hospital.eval_restrictions()["score"] == 50


def test_mobility_assistance(hospital):
    hospital.wards[0].restrictions = [R.NoMobilityAssistance(50)]

    patient_bad_mobility = Patient(
        "p0",
        sex="female",
        weight=80,
        department="surgery",
        needs_mobility_assistence=True,
    )
    hospital.admit(patient_bad_mobility, hospital.beds[0].name)
    assert patient_bad_mobility in hospital.patients
    assert hospital.eval_restrictions()["score"] == 50
    hospital.clear()

    patient_good_mobility = Patient(
        "p1",
        sex="female",
        weight=80,
        department="surgery",
        needs_mobility_assistence=False,
    )
    hospital.admit(patient_good_mobility, hospital.beds[0].name)
    assert patient_good_mobility in hospital.patients
    assert hospital.eval_restrictions()["score"] == 0
    hospital.clear()


def test_dementia_risk(hospital):
    hospital.wards[0].restrictions = [R.NoDementiaRisk(80)]

    patient_with_dementia = Patient(
        "p0",
        sex="female",
        department="surgery",
        is_dementia_risk=True,
    )
    hospital.admit(patient_with_dementia, hospital.beds[0].name)
    assert patient_with_dementia in hospital.patients
    hospital.clear()

    patient_no_dementia = Patient(
        "p1",
        sex="female",
        weight=80,
        department="surgery",
        is_dementia_risk=False,
    )
    hospital.admit(patient_no_dementia, hospital.beds[0].name)
    assert patient_no_dementia in hospital.patients
    assert hospital.eval_restrictions()["score"] == 0
    hospital.clear()


def test_high_acuity_patients(hospital):
    hospital.wards[0].restrictions = [R.NoHighAcuity(100)]

    patient_high_acuity = Patient(
        "p0",
        sex="female",
        weight=80,
        department="surgery",
        is_high_acuity=True,
    )
    hospital.admit(patient_high_acuity, hospital.beds[0].name)
    assert hospital.eval_restrictions()["score"] == 100
    hospital.clear()

    patient_low_acuity = Patient(
        "p0",
        sex="female",
        department="surgery",
        is_high_acuity=False,
    )
    hospital.admit(patient_low_acuity, hospital.beds[0].name)
    assert hospital.eval_restrictions()["score"] == 0


def test_no_non_elective(hospital):
    hospital.wards[0].restrictions = [R.NoNonElective(100)]

    patient_elective = Patient(
        "p0",
        sex="female",
        weight=80,
        department="surgery",
        is_elective=True,
    )
    hospital.admit(patient_elective, hospital.beds[0].name)
    assert hospital.eval_restrictions()["score"] == 0
    hospital.clear()

    patient_non_elective = Patient(
        "p0",
        sex="female",
        weight=80,
        department="surgery",
        is_elective=False,
    )
    hospital.admit(patient_non_elective, hospital.beds[0].name)
    assert hospital.eval_restrictions()["score"] == 100
    hospital.clear()


def test_no_surgical(hospital):
    hospital.wards[0].restrictions = [R.NoSurgical(50)]

    patient_surgical = Patient(
        "p0", sex="female", weight=80, department="surgery"
    )
    hospital.admit(patient_surgical, hospital.beds[0].name)
    assert hospital.eval_restrictions()["score"] == 50
    hospital.clear()

    patient_medical = Patient(
        "p0", sex="female", weight=80, department="medicine"
    )
    hospital.admit(patient_medical, hospital.beds[0].name)
    assert hospital.eval_restrictions()["score"] == 0
    hospital.clear()


def test_no_medical(hospital):
    hospital.wards[0].restrictions = [R.NoMedical(50)]

    patient_medical = Patient(
        "p0", sex="female", weight=80, department="medicine"
    )
    hospital.admit(patient_medical, hospital.beds[0].name)
    assert hospital.eval_restrictions()["score"] == 50
    hospital.clear()

    patient_surgical = Patient(
        "p0", sex="female", weight=80, department="surgery"
    )
    hospital.admit(patient_surgical, hospital.beds[0].name)
    assert hospital.eval_restrictions()["score"] == 0
    hospital.clear()


def test_ward_specialties(hospital):

    patient_cardiology = Patient(
        "p_cariology",
        sex="female",
        weight=80,
        department="surgery",
        specialty="cardiology",
    )

    patient_orthopaedic = Patient(
        "_orthopaedic",
        sex="female",
        weight=80,
        department="surgery",
        specialty="trauma_and_orthopaedic",
    )

    hospital.wards[0].specialty = [
        Specialty.trauma_and_orthopaedic,
        Specialty.general,
    ]
    hospital.wards[0].restrictions = [R.IncorrectSpecialty(50)]

    hospital.admit(patient_cardiology, hospital.beds[0].name)
    assert hospital.eval_restrictions()["score"] == 50
    hospital.clear()

    hospital.admit(patient_orthopaedic, hospital.beds[0].name)
    assert hospital.eval_restrictions()["score"] == 0
    hospital.clear()
