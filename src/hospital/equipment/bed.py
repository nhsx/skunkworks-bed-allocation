from anytree import NodeMixin

from hospital.exceptions import BedOccupiedError


class Bed(NodeMixin):
    """
    Base class for Beds in virtual hospital.

    Attributes
    ----------
    name: str
        Name of room.
    room: hospital.building.room.Room
        Room is parent of the bed. This can be any of the Room classes defined
        in hospital.building.room. It is the parent of the bed within the tree
        structure.
    patient: hospital.people.Patient
        Patient assigned to bed. If None then bed is considered unoccupied.
    """

    aliases = {"room": "parent"}

    def __init__(self, name, room=None, patient=None):
        super(Bed, self).__init__()
        self.name = name
        self.parent = room
        self.patient = patient

    def allocate(self, patient):
        if self.patient is not None:
            msg = f"Bed {self} is alreay in use."
            raise BedOccupiedError(msg)
        self.patient = patient

    def vacate(self):
        p = self.patient
        self.patient = None
        return p

    @property
    def is_available(self):
        return self.patient is None

    @property
    def is_occupied(self):
        return not self.is_available

    def __setattr__(self, name, value):
        name = self.aliases.get(name, name)
        object.__setattr__(self, name, value)

    def __getattr__(self, name):
        if name == "aliases":
            raise AttributeError
        name = self.aliases.get(name, name)
        # return getattr(self, name)
        return object.__getattribute__(self, name)

    def __repr__(self):
        cls = self.__class__.__name__
        return f"{cls}(name={self.name}, patient={self.patient})"


class HighVisibility(Bed):
    pass
