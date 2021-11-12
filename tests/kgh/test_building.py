"""
Test suite for hospital.building module.
"""
import pytest

from hospital.building.building import Hospital
from hospital.building.room import Room
from hospital.building.ward import Ward
from hospital.equipment.bed import Bed
from hospital.people import Patient


@pytest.fixture
def hospital():
    return Hospital("H")


@pytest.fixture
def ward():
    return Ward(name="W0", sex="female")


@pytest.fixture
def room():
    return Room(name="R0")


@pytest.fixture
def bed_():
    return Bed(name="B0")


@pytest.fixture
def patient():
    return Patient(
        name="John Sena",
        sex="male",
        weight=98,
        department="surgery",
        is_known_covid=False,
        is_suspected_covid=True,
    )


def test_room(room, bed_, patient):
    assert room.ward is None
    assert room.beds == ()
    assert room.patients == ()
    bed_.allocate(patient)
    room.beds = [bed_]
    assert room.patients == (patient,)
    bed_.vacate()
    assert room.patients == ()


def test_ward(hospital, ward, room, bed_, patient):
    assert ward.hospital is None
    assert ward.rooms == ()
    assert ward.beds == ()
    assert ward.patients == ()
    bed_.allocate(patient)
    room.beds = [
        bed_,
    ]
    ward.rooms = [
        room,
    ]
    assert ward.patients == (patient,)
    bed_.vacate()
    assert ward.patients == ()


def test_hospital(hospital, ward, room, bed_, patient):
    assert hospital.wards == ()
    assert hospital.rooms == ()
    assert hospital.beds == ()
    assert hospital.patients == ()
    bed_.room = room
    room.ward = ward
    ward.hospital = hospital
    hospital.admit(patient, bed_.name)
    assert hospital.patients == (patient,)
    assert hospital.find_patient(patient) == bed_


def test_ward_restrictions(ward, patient):
    assert ward.eval_restrictions()["score"] == 0
