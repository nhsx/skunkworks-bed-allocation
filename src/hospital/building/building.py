from functools import reduce

from anytree import NodeMixin, RenderTree

from hospital.exceptions import BedNotFoundError, PatientNotFoundError


class Hospital(NodeMixin):
    """
    Hospital class for the virtual hospital.

    Attributes
    ----------
    name: str
        Name of Hospital.
    wards: List[hospital.building.ward.Ward]
        Wards are children of the Hospital. They can be or any type within
        hospital.building.ward.
    """

    aliases = {"wards": "children"}

    def __init__(self, name, wards=None):
        super(Hospital, self).__init__()
        self.name = name
        if wards:
            self.children = wards

    def admit(self, patient, bed_name):
        bed = self.find_bed(bed_name)
        bed.allocate(patient)
        patient.allocate(bed)

    def discharge(self, patient):
        bed = self.find_patient(patient)
        bed.vacate()
        patient.discharge()

    def find_bed(self, bed_name):
        try:
            result = next(bed for bed in self.beds if bed.name == bed_name)
        except StopIteration:
            message = f"Couldn't find any bed with name {bed_name}"
            raise BedNotFoundError(message)
        else:
            return result

    def find_patient(self, patient):
        try:
            result = next(bed for bed in self.beds if bed.patient == patient)
        except StopIteration:
            message = f"Couldn't find patient {patient} in any bed."
            raise PatientNotFoundError(message)
        else:
            return result

    def render(self, maxlevel=None):
        for pre, _, node in RenderTree(self, maxlevel=maxlevel):
            patient = getattr(node, "patient", None)
            name = getattr(patient, "name", "")
            occupied = f":{name}" if name else ""
            print(f"{pre!s}{node.name}{occupied}")

    def eval_restrictions(self):
        """
        Returns the total penalty and a list of violated
        restrictions within the hospital.
        """
        penalties = []
        names = []
        entities = self.wards + self.rooms + self.patients
        for e in entities:
            penalties.append(e.eval_restrictions()["score"])
            names += e.eval_restrictions()["names"]

        return {"score": sum(penalties), "names": names}

    def clear(self):
        for bed in self.get_occupied_beds():
            patient = bed.patient
            bed.vacate()
            patient.discharge()

    def get_empty_beds(self):
        return (bed for bed in self.beds if bed.is_available)

    def get_occupied_beds(self):
        return (bed for bed in self.beds if bed.is_occupied)

    def has_empty_beds(self):
        return any(bed.is_available for bed in self.beds)

    def __setattr__(self, name, value):
        name = self.aliases.get(name, name)
        object.__setattr__(self, name, value)

    def __getattr__(self, name):
        if name == "aliases":
            raise AttributeError
        name = self.aliases.get(name, name)
        return object.__getattribute__(self, name)

    @property
    def rooms(self):
        add = tuple.__add__
        gen = (ward.rooms for ward in self.wards)
        return reduce(add, gen, ())

    @property
    def beds(self):
        add = tuple.__add__
        gen = (room.beds for room in self.rooms)
        return reduce(add, gen, ())

    @property
    def patients(self):
        return tuple(
            bed.patient for bed in self.beds if bed.patient is not None
        )

    def __repr__(self):
        cls = self.__class__.__name__
        return f"<{cls}(name={self.name})>"
