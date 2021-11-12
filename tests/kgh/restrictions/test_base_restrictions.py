"""
Test suite for the `hospital.restrictions.base` module.
"""

from hospital.building.room import SideRoom
from hospital.equipment.bed import Bed
from hospital.people import Patient
from hospital.restrictions.room import KeepSideRoomEmpty
from hospital.restrictions.ward import NoAcuteSurgical


def test_change_penality():
    patient = Patient(
        name="p1",
        sex="male",
        department="medicine",
        is_immunosupressed=True,
    )
    assert patient.restrictions[0].penalty == 10

    patient.restrictions[0].change_penalty(20)

    assert patient.restrictions[0].penalty == 20


def test_combining_multiple_restriction_types(hospital):
    """
    This is a test to check that different types of restrictions are
    summed together corretly when hospital.eval_restrictions() is called and
    that the returned list of violated restrictions is correct.
    """
    hospital.wards[0].restrictions = [
        NoAcuteSurgical(10),
    ]

    # try a ward level restriction
    p_surgical = Patient(
        name="surgical",
        sex="female",
        department="surgery",
        is_acute_surgical=True,
    )
    hospital.admit(p_surgical, hospital.beds[0].name)
    assert hospital.eval_restrictions()["score"] == 10
    assert hospital.eval_restrictions()["names"] == ["NoAcuteSurgical"]

    # try a room level restriction
    sideroom = SideRoom(
        name="sideroom",
        ward=hospital.wards[0],
        restrictions=[KeepSideRoomEmpty(10)],
    )
    bed2 = Bed("B002", room=sideroom)
    p_default = Patient(name="acute", sex="female", department="surgery")
    hospital.admit(p_default, bed2.name)
    assert hospital.eval_restrictions()["score"] == 20
    assert hospital.eval_restrictions()["names"] == [
        "NoAcuteSurgical",
        "KeepSideRoomEmpty",
    ]

    # try a patient level restriction (Fixed penalty for immunosupressed if 10)
    bed3 = Bed("B003", room=hospital.rooms[0])
    p_sideroom = Patient(
        name="needs_sideroom",
        sex="female",
        department="surgery",
        is_immunosupressed=True,
    )
    hospital.admit(p_sideroom, bed3.name)
    assert p_sideroom.restrictions[0].penalty == 10
    assert hospital.eval_restrictions()["score"] == 30
    assert hospital.eval_restrictions()["names"] == [
        "NoAcuteSurgical",
        "KeepSideRoomEmpty",
        "NeedsSideRoom",
    ]
