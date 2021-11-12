"""
Test suite for the `hospital.equipment` module.
"""
import pytest

from hospital.equipment import bed
from hospital.exceptions import BedOccupiedError
from hospital.people import Patient


@pytest.fixture
def patient():
    return Patient(
        name="John Sena",
        sex="male",
        weight=98,
        department="medicine",
        is_known_covid=False,
        is_suspected_covid=True,
    )


@pytest.mark.parametrize(
    "bed_type",
    [
        bed.HighVisibility,
    ],
)
def test_bed(bed_type, patient):
    b = bed_type(name="B0", patient=None, room=None)
    b.allocate(patient)
    assert b.patient == patient
    with pytest.raises(BedOccupiedError):
        b.allocate(patient)
    b.vacate()
    assert b.patient is None
