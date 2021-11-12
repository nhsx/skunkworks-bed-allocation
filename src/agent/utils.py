import math
import random
from collections import Counter
from typing import Generator

import numpy as np

from forecasting.patient_sampler import (
    fill_magnets,
    filter_patients,
    generate_random_patients,
    pandas_to_patients,
)
from hospital.building import Hospital
from hospital.people import Patient


def logistic(x: float):
    """Logistic function."""
    return 1 / (1 + math.exp(-x))


def bernoulli(p: float):
    """
    Draw a sample from a bernoulli distribution with parameter `p`.
    """
    return random.choices([0, 1], weights=[1 - p, p])[0]


def generate_random_patient() -> Patient:
    """
    Generate a random synthetic patient.
    """
    patient_sample = generate_random_patients(
        1,
        np.random.choice([day for day in range(0, 7)]),
        np.random.choice([hour for hour in range(0, 24)]),
    )
    patient_sample = filter_patients(patient_sample)
    patient_sample = fill_magnets(patient_sample)
    patient = pandas_to_patients(patient_sample)
    return patient


def normalise_ward_penalties(hospital: Hospital) -> Hospital:
    """
    Normalises the ward penaltied by the maximum possible
    penalty for the hospital.
    """
    max_penalty = 0
    for ward in hospital.wards:
        for restriction in ward.restrictions:
            max_penalty += sum(restriction.penalty for _ in ward.beds)

    for ward in hospital.wards:
        for restriction in ward.restrictions:
            restriction.penalty /= max_penalty


def arrivals_generator(arrivals_list: list) -> Generator:
    """
    Generates patients from the list of arrivals at a given timestep.
    """
    for patient in arrivals_list:
        yield patient


def reduce_restrictions(
    base_restrictions: list, new_restrictions: list
) -> list:
    """
    Compares lists of restrictions returns the set difference,
    accounting for repeatitions.
    """
    if base_restrictions and not base_restrictions == new_restrictions:
        return list(
            (Counter(new_restrictions) - Counter(base_restrictions)).elements()
        )
    elif base_restrictions == new_restrictions:
        return []
    else:
        return new_restrictions


def assign_best_action(
    hospital: Hospital, ordered_mcts_output: dict
) -> Hospital:
    """
    Admits patients to beds according to the best action.
    """
    best_action = ordered_mcts_output[0].get("action", None)
    if best_action:
        for bed, patient in best_action.items():
            hospital.admit(patient, bed)
    return hospital
