from enum import Enum, auto


class Sex(Enum):
    female = 0
    male = 1
    unknown = 2


class Department(Enum):
    medicine = "medicine"
    surgery = "surgery"


class Specialty(Enum):
    trauma_and_orthopaedic = auto()
    general = auto()
    respiratory = auto()
    gastroenterology = auto()
    endocrinology = auto()
    cardiology = auto()
    elderly_care = auto()
