from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any, Dict, Optional
from warnings import warn

import hospital.restrictions.people as R
from hospital.data import Department, Sex, Specialty
from hospital.equipment.bed import Bed


@dataclass
class Patient:
    """
    Patient dataclass
    """

    name: str
    sex: str
    department: str
    specialty: str = "general"
    weight: float = 70.0
    age: Optional[int] = None
    is_known_covid: bool = False
    is_suspected_covid: bool = False
    is_acute_surgical: bool = False  # TODO remove(redundant with high acuity)
    is_elective: bool = False
    needs_mobility_assistence: bool = False
    is_dementia_risk: bool = False
    is_high_acuity: bool = False
    is_immunosupressed: bool = False
    is_end_of_life: bool = False
    is_infection_control: bool = False
    is_falls_risk: bool = False
    needs_visual_supervision: bool = False

    expected_length_of_stay: int = 1
    length_of_stay: int = 0

    bed: Optional[Bed] = None
    restrictions: list = field(default_factory=list)

    def __post_init__(self):
        # convert and validate enums
        self.sex = self._validate_enums(self.sex, Sex)
        self.department = self._validate_enums(self.department, Department)
        self.specialty = self._validate_enums(self.specialty, Specialty)

        # initialise restrictions
        if self.is_immunosupressed:
            self.restrictions.append(R.NeedsSideRoom(10))
        if self.is_end_of_life:
            self.restrictions.append(R.NeedsSideRoom(3))
        if self.is_infection_control:
            self.restrictions.append(R.NeedsSideRoom(4))
        if self.is_falls_risk:
            self.restrictions.append(R.ProhibitedSideRoom(5))
        if self.needs_visual_supervision:
            self.restrictions.append(R.NeedsVisualSupervision(5))

    def _validate_enums(self, value, enum_class):
        try:
            return enum_class[value.lower()]
        except KeyError:
            print(
                f"Incorrect value for {enum_class.__name__.lower()} ",
                f"attribute : {value}",
            )

    def eval_restrictions(self):
        penalty = 0
        names = []
        for r in self.restrictions:
            total_penalty = r.evaluate(self)
            if total_penalty > 0:
                n, p = r._key()
                penalty += total_penalty
                names += [n for _ in range(int(total_penalty / p))]
        return {"score": penalty, "names": names}

    def allocate(self, bed):
        if self.bed is not None:
            warn(f"Patient {self.name} is already in bed {self.bed.name}.")
        self.bed = bed

    def discharge(self):
        self.bed = None


def patient_to_dict(patient: Patient) -> Dict[str, Any]:
    """
    Returns dictionary representation of a Patient class instance.
    """

    def _patient_dict(patient: Patient) -> Dict[str, Any]:
        """
        Dictionary factory to convert Patient class instance
        to patient details dictionary.
        """
        return {
            field: (value if not isinstance(value, Enum) else value.name)
            for field, value in patient
        }

    return asdict(patient, dict_factory=_patient_dict)
