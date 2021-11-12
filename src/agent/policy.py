import queue
import random
from collections import defaultdict
from operator import itemgetter

from agent.utils import generate_random_patient, reduce_restrictions
from hospital.building.building import Hospital
from hospital.building.room import BedBay, SideRoom
from hospital.people import Patient


def random_allocate(
    hospital: Hospital, patient_queue: queue.Queue, random_seed: int = None
):
    """
    Random allocation policy. While there are beds available and patients in
    the queue, allocate them to a random empty bed.

    Parameters
    ----------
    hospital: Hospital
        An instance of the hospital class.

    patient_queue: queue
        A queue of Patient class instances.
    """
    random.seed(random_seed)

    empty_beds = list(hospital.get_empty_beds())
    random.shuffle(empty_beds)
    while True:
        try:
            patient = patient_queue.get_nowait()
            bed = empty_beds.pop()
        except (queue.Empty, IndexError):
            break
        else:
            bed.allocate(patient)


def greedy_allocate(hospital: Hospital, patient_queue: queue.Queue):
    """
    Greedy allocation policy. While there are beds available and patients in
    the queue, allocate them to the best empty bed.
    """
    while True:
        try:
            patient = patient_queue.get_nowait()
            best_bed = find_best_bed(patient, hospital)[0]
        except (queue.Empty, ValueError):
            break
        else:
            hospital.admit(patient, best_bed)


def greedy_suggestions(
    hospital: Hospital, patient: Patient, num_beds: int = 1
) -> dict:
    """
    Returns the top N (num_beds) greedy allocation suggestions for a patient
    as a dictionary where keys are the suggested bed name, and values are
    dictionaries containing the associated penalty and violated restrictions.
    """
    best_beds = find_best_bed(patient, hospital, num_beds)
    base_score, base_restrictions = itemgetter("score", "names")(
        hospital.eval_restrictions()
    )

    suggetions = {}
    for bed_name in best_beds:
        hospital.admit(patient, bed_name)
        new_state = hospital.eval_restrictions()
        suggetions[bed_name] = {
            "penalty": new_state["score"] - base_score,
            "violated_restrictions": reduce_restrictions(
                base_restrictions, new_state["names"]
            ),
        }
        hospital.discharge(patient)

    return suggetions


def populate_hospital(hospital: Hospital, occupancy: float):
    """
    Populates a hospital with patients upto an initial occupancy fraction.
    """
    total_beds = len(hospital.beds)
    while len(list(hospital.get_occupied_beds())) < int(
        total_beds * occupancy
    ):
        q = queue.Queue()
        patient = generate_random_patient()
        if patient:
            q.put(patient[0])
            random_allocate(hospital, q)


def find_best_bed(
    patient: Patient, hospital: Hospital, num_beds: int = 1
) -> list:
    """
    Returns the beds with the lowest penalty for a given patient.
    The number of beds returned is determined by the num_beds parameter.
    """
    beds = quotient_hospital(hospital)
    current_penalty = hospital.eval_restrictions()["score"]
    results = []
    for bed_name in beds.keys():
        hospital.admit(patient, bed_name)
        delta = hospital.eval_restrictions()["score"] - current_penalty
        hospital.discharge(patient)
        results.append((bed_name, delta))

    best = [
        bed_name
        for bed_name, score in sorted(results, key=lambda x: x[1])[:(num_beds)]
    ]
    return best


def _first(iterable, key=None):
    return sorted(iterable, key=key)[0]


def empty_ward_beds(hospital: Hospital) -> dict:
    """
    Returns a dictionary containing a list of empty bed for each ward.
    """
    beds_per_ward = defaultdict(list)
    for bed in hospital.get_empty_beds():
        beds_per_ward[bed.room.ward.name].append(bed)
    return beds_per_ward


def equivalent_beds(hospital: Hospital) -> dict:
    """
    Returns a dictionary containing a list of equivalent beds.
    Keys specify the location of the set of beds (ward or room).
    """
    equivalent_beds = defaultdict(list)
    for bed in hospital.get_empty_beds():
        if isinstance(bed.room, BedBay):
            # if there is a ward sex all beds in bays are equivalent.
            if bed.room.ward.sex.name in ["female", "male"]:
                equivalent_beds[bed.room.ward.name].append(bed)
            else:
                equivalent_beds[bed.room.name].append(bed)
        # sideroom beds are not equivalent to bed bay beds.
        # there may be more than one bed in a side room
        if isinstance(bed.room, SideRoom):
            equivalent_beds[bed.room.name].append(bed)
    return equivalent_beds


def quotient_hospital(hospital: Hospital) -> dict:
    """
    First empty bed in each location and the fraction
    of equivalent empty beds in the hospital.
    (`quotient` as in a 'quotient space' in mathematics)
    """
    eq_beds = equivalent_beds(hospital)
    representatives = {}
    for _, beds in eq_beds.items():
        bed = _first(beds, key=lambda x: x.name)
        representatives[bed.name] = len(beds)

    total = sum(representatives.values())
    return {k: v / total for k, v in representatives.items()}
