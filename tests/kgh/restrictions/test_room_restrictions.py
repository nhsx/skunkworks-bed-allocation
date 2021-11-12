"""
Test suite for the `hospital.restrictions.people` module.
"""

from hospital.equipment.bed import Bed
from hospital.people import Patient
from hospital.restrictions import room as R


def test_no_mixed_sex_room(hospital):
    hospital.wards[0].rooms[0].restrictions = [R.NoMixedSex(20)]

    male_1 = Patient(
        "male1",
        sex="male",
        weight=70,
        department="medicine",
    )
    male_2 = Patient(
        "male2",
        sex="male",
        weight=80,
        department="medicine",
    )
    female_1 = Patient(
        "female1",
        sex="female",
        weight=70,
        department="medicine",
    )
    female_2 = Patient(
        "female2",
        sex="female",
        weight=70,
        department="medicine",
    )

    # check all male room
    hospital.admit(male_1, hospital.beds[0].name)
    hospital.admit(male_2, hospital.beds[1].name)
    assert male_1.bed.room == male_2.bed.room
    assert hospital.eval_restrictions()["score"] == 0

    # check penalty for adding female
    bed3 = Bed("B3", room=male_1.bed.room)
    hospital.admit(female_1, bed3.name)
    assert female_1.bed.room == male_1.bed.room
    assert hospital.eval_restrictions()["score"] == 20

    # check penalty same for adding second female
    bed4 = Bed("B4", room=male_1.bed.room)
    hospital.admit(female_2, bed4.name)
    assert female_2.bed.room == male_1.bed.room
    assert hospital.eval_restrictions()["score"] == 20


def test_keep_sideroom_empty(hospital):
    patient = Patient(
        "p1",
        sex="male",
        weight=70,
        department="medicine",
    )

    # N.B. this should only really be applied to siderooms
    hospital.wards[0].rooms[0].restrictions = [R.KeepSideRoomEmpty(5)]

    hospital.admit(patient, hospital.beds[0].name)
    assert patient in hospital.rooms[0].patients
    assert hospital.eval_restrictions()["score"] == 5
