# This file was generated from notebooks/1.Virtual_Hospital_Environment.ipynb

# Import required modules

import cloudpickle

from hospital.equipment.bed import Bed
from hospital.building.room import BedBay, SideRoom
from hospital.building.ward import SurgicalWard, MedicalWard
from hospital.building.building import Hospital
from hospital.restrictions import ward as W
from hospital.restrictions import room as R
from hospital.people import Patient

# initialise hospital object
hospital = Hospital("H1")

# Setup Wards and restrictions
wards = [
    MedicalWard(
        name="Ward A",
        specialty=["general"],
        restrictions=[
            W.NoKnownCovid(10),
            W.NoSuspectedCovid(10),
            W.NoSurgical(3),
            W.IncorrectSpecialty(2),
        ],
        hospital=hospital,
    ),
    MedicalWard(
        name="Ward B",
        sex="female",
        specialty=["endocrinology"],
        restrictions=[
            W.NoKnownCovid(10),
            W.NoSuspectedCovid(10),
            W.NoSurgical(3),
            W.IncorrectSpecialty(2),
            W.IncorrectSex(10),
        ],
        hospital=hospital,
    ),
    MedicalWard(
        name="Ward C",
        sex="male",
        specialty=["endocrinology"],
        restrictions=[
            W.NoKnownCovid(10),
            W.NoSuspectedCovid(10),
            W.NoSurgical(3),
            W.IncorrectSpecialty(2),
            W.IncorrectSex(10),
        ],
        hospital=hospital,
    ),
    MedicalWard(
        name="Ward D",
        specialty=["Respiratory"],
        restrictions=[
            W.NoNonCovid(10),
            W.NoSurgical(3),
            W.IncorrectSpecialty(2),
        ],
        hospital=hospital,
    ),
    SurgicalWard(
        name="Ward E",
        department="surgery",
        specialty=["general"],
        restrictions=[
            W.NoKnownCovid(10),
            W.NoSuspectedCovid(10),
            W.NoMedical(1),
            W.IncorrectSpecialty(2),
            W.NoAcuteSurgical(8),
        ],
        hospital=hospital,
    ),
    SurgicalWard(
        name="Ward F",
        department="surgery",
        specialty=["trauma_and_orthopaedic"],
        restrictions=[
            W.NoKnownCovid(10),
            W.NoSuspectedCovid(10),
            W.NoMedical(1),
            W.IncorrectSpecialty(2),
            W.NoAcuteSurgical(8),
        ],
        hospital=hospital,
    ),
]

# check wards in hospital
hospital.wards

# Create an iterator of IDs to avoid duplicating names
ROOM_IDS = iter(f"R{str(n).zfill(2)}" for n in range(100))
BED_IDS = iter((f"B{str(n).zfill(3)}" for n in range(1000)))

# define the number of beds and siderooms for each ward
WARD_TO_ROOMS = {
    "Ward A": {"beds": 31, "siderooms": 2},
    "Ward B": {"beds": 27, "siderooms": 6},
    "Ward C": {"beds": 27, "siderooms": 6},
    "Ward D": {"beds": 18, "siderooms": 2},
    "Ward E": {"beds": 24, "siderooms": 0},
    "Ward F": {"beds": 27, "siderooms": 3},
}


def generate_rooms(ward, ward_to_room_map, room_ids, bed_ids):
    """
    Generate side rooms and bed bays  and beds for a ward.
    """
    rooms = []
    # add siderooms
    for sideroom in range(ward_to_room_map[ward.name]["siderooms"]):
        rooms.append(
            SideRoom(
                name=next(room_ids),
                beds=[Bed(name=next(bed_ids))],
                ward=ward,
            )
        )

    # add bed bays
    total_beds = (
        ward_to_room_map[ward.name]["beds"]
        - ward_to_room_map[ward.name]["siderooms"]
    )
    num_bays = total_beds // 6
    bed_bay_numbers = [
        total_beds // num_bays + (1 if x < total_beds % num_bays else 0)
        for x in range(num_bays)
    ]
    for num_beds in bed_bay_numbers:
        rooms.append(
            BedBay(
                name=next(room_ids),
                beds=[Bed(name=next(bed_ids)) for i in range(num_beds)],
                # NoMixedSex restriction applies to all bed bays
                restrictions=[R.NoMixedSex(8)],
                ward=ward,
            )
        )
    return rooms


for ward in wards:
    ward_rooms = {}
    ward_rooms[ward.name] = generate_rooms(
        ward, WARD_TO_ROOMS, ROOM_IDS, BED_IDS
    )

print(f"Rooms: {len(hospital.rooms)},Beds: {len(hospital.beds)}")

# Save hospital
with open("../../data/hospital.pkl", "wb") as f:
    cloudpickle.dump(hospital, f)
    print("hospital.pkl saved")
