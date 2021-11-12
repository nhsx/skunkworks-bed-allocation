import abc


class BaseRestriction(abc.ABC):
    """
    Base class for all restrictions.
    """

    def __init__(self, penalty=0):
        self.penalty = penalty

    def __repr__(self):
        cls = self.__class__.__name__
        return f"{cls}(penalty={self.penalty})"

    def __eq__(self, other):
        self_cls = self.__class__.__name__
        other_cls = other.__class__.__name__
        names_match = self_cls == other_cls
        penalties_match = self.penalty == other.penalty
        return names_match and penalties_match

    def __hash__(self):
        return hash(self._key())

    def _key(self):
        cls = self.__class__.__name__
        val = self.penalty
        return (cls, val)

    def change_penalty(self, new_penalty):
        setattr(self, "penalty", new_penalty)


class WardRestriction(BaseRestriction):
    """
    Base class for ward level restrictions. These restrictions are evaluated
    for each bed, the total penalty is the sum across all bed within the ward.

    Wards can be initialised with the desired restrictions and penalties:
    `ward = Ward(
        name=name,
        rooms=rooms,
        restrictions=[NameOfRestriction(penalty)]
        )`
    Ward restrictions can also be appended of modified later:
    `ward.restrictions.append(NameOfRestriction(penalty))`
    `ward.restrictions[0].change_penalty(new_panalty)`
    """

    def evaluate(self, ward):
        """
        Scan through beds in the ward and penalize
        violations to the restriction
        """
        return sum(self._evaluate_bed(bed) for bed in ward.beds)

    @abc.abstractmethod
    def _evaluate_bed(self, bed):
        """
        Determine the penalty for the bed in question.
        """


class RoomRestriction(BaseRestriction):
    """
    Base class for room level restrictions. These restrictions are evaluated
    based on the state of the entire room/bed bay. For example,
    adding a female patient to an all male room will incur the penalty once,
    rather than multiple times for each occupied bed.

    Rooms can be initialised with the desired restrictions and penalties:
    `room = Room(
        name=name,
        beds=beds,
        restrictions=[NameOfRestriction(penalty)]
        )`
    Room restrictions can also be appended of modified later:
    `room.restrictions.append(NameOfRestriction(penalty))`
    `room.restrictions[0].change_penalty(new_panalty)`
    """

    def evaluate(self, room):
        """
        Evaluate the room level restriction.
        """
        return self._evaluate_room(room)

    @abc.abstractclassmethod
    def _evaluate_room(self, room):
        """
        Determine the penalty for the room in question.
        """


class PatientRestriction(BaseRestriction):
    """
    Base class for patient level restrictions. These restrictions evaluated
    based on the bed/room/ward allocated to a patient. For example, if the
    patient needed to be in a sideroom but was assigned to a shared
    bedbay a penalty will incur.

    Patients are automatically initalised with relevent restrictions and
    their associated penalties based on key attributes. The penalties can be
    modified:
    `patient.restrictions[0].change_penalty(new_penalty)`
    """

    def evaluate(self, patient):
        """
        Evaluate the patient level restriction.
        """
        return self._evaluate_patient(patient)

    @abc.abstractclassmethod
    def _evaluate_patient(self, patient):
        """
        Determine the penalty for the bed in question.
        """
