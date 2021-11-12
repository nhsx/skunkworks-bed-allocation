from functools import reduce

from anytree import NodeMixin

from hospital.data import Department, Sex, Specialty


class Ward(NodeMixin):
    """
    Base class for all kind of wards in virtual hospital.

    Attributes
    ----------
    name: str
        Name of ward.
    sex: str
        Ward sex (female, male, unknown). Input as string values are validated
        and converted to Enums (hospital.data.Sex) upon initialisation.
    department: str
        Ward department (medicine, surgey). Input as string values are
        validated and converted to Enums (hospital.data.Department) upon
        initialisation. Default value is medicine.
    specialty: List[str], optional
        Ward specialty (general, cardiology etc.,) Input as string values are
        validated and converted to Enums (hospital.data.Specialty) upon
        initialisation.
    restrictions: List[hospital.restrictions.base.WardRestrictions], optional
        List of applicable ward restrictions.
    hospital: hospital.building.building.Hospital, optional
        Hospital is the parent of ward.
    rooms: List[hospital.building.room.Room]
        Rooms are children of the Ward, and should be either BedBays and
        Siderooms.
    """

    aliases = {
        "hospital": "parent",
        "rooms": "children",
    }

    def __init__(
        self,
        name,
        sex="unknown",
        department="medicine",
        specialty=[],
        restrictions=None,
        hospital=None,
        rooms=None,
    ):
        super(Ward, self).__init__()
        self.name = name
        self.sex = self._validate_enum(sex, Sex)
        self.specialty = [self._validate_enum(s, Specialty) for s in specialty]
        self.department = self._validate_enum(department, Department)
        self.parent = hospital
        if rooms:
            self.children = rooms

        self.restrictions = restrictions or []

    def _validate_enum(self, value, enum_class):
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

    def __setattr__(self, name, value):
        name = self.aliases.get(name, name)
        object.__setattr__(self, name, value)

    def __getattr__(self, name):
        if name == "aliases":
            raise AttributeError
        name = self.aliases.get(name, name)
        return object.__getattribute__(self, name)

    @property
    def beds(self):
        add = tuple.__add__
        gen = (room.beds for room in self.rooms)
        return reduce(add, gen, ())

    @property
    def empty_beds(self):
        return [bed for bed in self.beds if bed.patient is None]

    @property
    def patients(self):
        return tuple(
            bed.patient for bed in self.beds if bed.patient is not None
        )

    def __repr__(self):
        cls = self.__class__.__name__
        return f"<{cls}(name={self.name})>"


class SurgicalWard(Ward):
    """Surgical ward."""

    def __init__(
        self,
        name,
        sex="unknown",
        department="surgery",
        specialty=[],
        restrictions=None,
        hospital=None,
        rooms=None,
    ):
        super().__init__(
            name, sex, department, specialty, restrictions, hospital, rooms
        )


class MedicalWard(Ward):
    """Medical ward."""

    pass
