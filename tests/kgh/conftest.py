import pytest

from hospital.building import Hospital, Room, Ward
from hospital.equipment.bed import Bed


@pytest.fixture
def hospital():
    beds = [Bed("B0"), Bed("B1")]
    rooms = [Room("R0", beds=beds)]
    wards = [Ward("W0", rooms=rooms)]
    return Hospital("H", wards=wards)
