"""
Test suite for the `hospital.restrictions.people` module.
"""

from hospital.building.room import SideRoom
from hospital.equipment.bed import Bed, HighVisibility
from hospital.people import Patient
from hospital.restrictions import people as R


def test_immunosuppressed_sideroom(hospital):
    patient = Patient(
        name="p1",
        sex="male",
        weight=60.7,
        department="medicine",
        is_immunosupressed=True,
    )
    assert patient.restrictions == [R.NeedsSideRoom(10)]

    hospital.admit(patient, hospital.beds[0].name)
    assert patient in hospital.patients
    assert hospital.eval_restrictions()["score"] == 10
    hospital.clear()

    sideroom = SideRoom(
        "sideroom", ward=hospital.wards[0], beds=[Bed("sideroom_bed")]
    )
    assert sideroom in hospital.rooms

    hospital.admit(patient, "sideroom_bed")
    assert patient in hospital.patients
    assert hospital.eval_restrictions()["score"] == 0


def test_end_of_life_sideroom(hospital):
    patient = Patient(
        name="eol",
        sex="male",
        weight=60.7,
        department="medicine",
        is_end_of_life=True,
    )
    assert patient.restrictions == [R.NeedsSideRoom(3)]

    hospital.admit(patient, hospital.beds[0].name)
    assert patient in hospital.patients
    assert hospital.eval_restrictions()["score"] == 3
    hospital.clear()

    sideroom = SideRoom(
        "sideroom", ward=hospital.wards[0], beds=[Bed("sideroom_bed")]
    )
    assert sideroom in hospital.rooms

    hospital.admit(patient, "sideroom_bed")
    assert patient in hospital.patients
    assert hospital.eval_restrictions()["score"] == 0


def test_infection_control_sideroom(hospital):
    patient = Patient(
        name="eol",
        sex="male",
        weight=60.7,
        department="medicine",
        is_infection_control=True,
    )
    assert patient.restrictions == [R.NeedsSideRoom(4)]

    hospital.admit(patient, hospital.beds[0].name)
    assert patient in hospital.patients

    assert hospital.eval_restrictions()["score"] == 4
    hospital.clear()

    sideroom = SideRoom(
        "sideroom", ward=hospital.wards[0], beds=[Bed("sideroom_bed")]
    )
    assert sideroom in hospital.rooms

    hospital.admit(patient, "sideroom_bed")
    assert patient in hospital.patients
    assert hospital.eval_restrictions()["score"] == 0


def test_multiple_reasons_sideroom(hospital):
    patient = Patient(
        name="eol",
        sex="male",
        department="medicine",
        is_infection_control=True,
        is_end_of_life=True,
    )
    assert set(patient.restrictions) == set(
        [R.NeedsSideRoom(4), R.NeedsSideRoom(3)]
    )

    hospital.admit(patient, hospital.beds[0].name)
    assert patient in hospital.patients

    assert hospital.eval_restrictions()["score"] == 7
    hospital.clear()

    sideroom = SideRoom(
        "sideroom", ward=hospital.wards[0], beds=[Bed("sideroom_bed")]
    )
    assert sideroom in hospital.rooms

    hospital.admit(patient, "sideroom_bed")
    assert patient in hospital.patients
    assert hospital.eval_restrictions()["score"] == 0


def test_does_not_need_side_room(hospital):
    patient = Patient(
        name="p1",
        sex="male",
        weight=60.0,
        department="medicine",
    )

    assert patient.restrictions == []

    hospital.admit(patient, hospital.beds[0].name)
    assert patient in hospital.patients
    assert hospital.eval_restrictions()["score"] == 0
    hospital.clear()

    sideroom = SideRoom(
        "sideroom", ward=hospital.wards[0], beds=[Bed("sideroom_bed")]
    )
    assert sideroom in hospital.rooms

    # There is currently no penalty for admitting a patient
    # that does not specifically need a side room into one.
    hospital.admit(patient, "sideroom_bed")
    assert patient in hospital.patients
    assert hospital.eval_restrictions()["score"] == 0


def test_falls_risk_prohibited_sideroom(hospital):
    patient = Patient(
        name="p1",
        sex="male",
        weight=60.0,
        department="medicine",
        is_falls_risk=True,
    )
    assert patient.restrictions == [R.ProhibitedSideRoom(5)]

    hospital.admit(patient, hospital.beds[0].name)
    assert patient in hospital.patients
    assert hospital.eval_restrictions()["score"] == 0
    hospital.clear()

    sideroom = SideRoom(
        "sideroom", ward=hospital.wards[0], beds=[Bed("sideroom_bed")]
    )
    assert sideroom in hospital.rooms
    hospital.admit(patient, "sideroom_bed")
    assert patient in hospital.patients
    assert hospital.eval_restrictions()["score"] == 5


def test_needs_visual_supervision_bed(hospital):
    patient = Patient(
        name="p1",
        sex="female",
        weight=70.0,
        department="surgey",
        needs_visual_supervision=True,
    )
    assert patient.restrictions == [R.NeedsVisualSupervision(5)]

    hospital.admit(patient, hospital.beds[0].name)
    assert patient in hospital.patients
    assert hospital.eval_restrictions()["score"] == 5
    hospital.clear()

    visible_bed = HighVisibility(name="visible", room=hospital.rooms[0])
    assert visible_bed in hospital.beds
    hospital.admit(patient, "visible")
    assert patient in hospital.patients
    assert hospital.eval_restrictions()["score"] == 0
