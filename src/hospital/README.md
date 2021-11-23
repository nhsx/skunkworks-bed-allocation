# Virtual Hospital

## Introduction

The virtual hospital environment comprises several components that can be tailored to mimic any arbitrary hospital structure, allowing the user to test the allocation agents at different scales. It is based on a tree-like structure using the [anytree library](https://pypi.org/project/anytree/) to define the hierarchical structure of a hospital. 

The user can build virtual hospitals containing the desired number of wards, rooms and beds. In addition, the virtual hospital encodes the allocation restrictions and associated penalties that apply to the hospital, as well as the data structure for patients. We have encoded different types of ward (medical, surgical) and rooms (bed bays, side rooms) to cater for a broad range of allocation rules. In addition, certain restrictions apply specifically to a patient and are thus contained within the patient class (e.g. if a patient requires a sideroom).

This document is also available as a [notebook](../notebooks/1.Virtual_Hospital_Environment.ipynb).

## Create a Hospital

In this example, our hospital will consist of 4 medical wards and 2 surgical wards as detailed below. Within each ward we will add a number of rooms (bed bays and side rooms) as well as ward and room restrictions.

### Import required modules

```python
import cloudpickle

from hospital.equipment.bed import Bed
from hospital.building.room import BedBay, SideRoom
from hospital.building.ward import SurgicalWard, MedicalWard
from hospital.building.building import Hospital
from hospital.restrictions import ward as W
from hospital.restrictions import room as R
from hospital.people import Patient
```

### Initialise the hospital

Initialise the hospital object with a name. We can then set up a list of ward definitions, where wards can either be medical or surgial. In addition a list of specialties can be added, as well as ward sex if applicable. Finally, we apply some ward level restrictions. A full set of available ward restrictions are within the [`hospital.restrictions.ward`](restrictions/ward.py) submodule. 

```python
# initialise hospital object
hospital = Hospital("H1")
```

### Create the wards

```python
# Setup Wards and restrictions
wards = [
    MedicalWard(
        name="Ward A",
        specialty=["general"],
        restrictions=[
            W.NoKnownCovid(10),
            W.NoSuspectedCovid(10),
            W.NoSurgical(3),
            W.IncorrectSpecialty(2)
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
```

### Add rooms and beds

Below we create a generator to yield ward names, a dictionary to define the number of beds and siderooms we wish to add to each ward and a helper function that generates the bed bays and siderooms. In this function each side room has a single bed and the remaining beds are split into bed bays with roughly 6 beds each but the user can define whatever configuration they desire. We also apply a NoMixedSex room restriction to all the bed bays, additional room level restrictions are available in the [`hospital.restrictions.room`](restrictions/room.py) sub module.

```python
# Create an iterator of IDs to avoid duplicating names
ROOM_IDS = iter(f"R{str(n).zfill(2)}" for n in range(100))
BED_IDS = iter((f"B{str(n).zfill(3)}" for n in range(1000)))

# define the number of beds and siderooms for each ward
WARD_TO_ROOMS = {
    "Ward A":{"beds":31, "siderooms":2},
    "Ward B":{"beds":27, "siderooms":6},
    "Ward C":{"beds":27, "siderooms":6},
    "Ward D":{"beds":18, "siderooms":2},
    "Ward E":{"beds":24, "siderooms":0},
    "Ward F":{"beds":27, "siderooms":3},
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
```

We can now interate through each ward and create the required rooms:

```python
for ward in wards:
    ward_rooms = {}
    ward_rooms[ward.name] = generate_rooms(ward, WARD_TO_ROOMS, ROOM_IDS, BED_IDS)
    
print(f"Rooms: {len(hospital.rooms)},Beds: {len(hospital.beds)}")
```

## Exporting the hospital

Now the hospital is generated, we can save it as a cloudpickle for further use:

```python
with open("../data/hospital.pkl", "wb") as f:
    cloudpickle.dump(hospital, f)
```