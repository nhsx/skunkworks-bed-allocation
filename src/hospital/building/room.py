from anytree import NodeMixin


class Room(NodeMixin):
    """
    Base class for all kind of rooms in virtual hospital.

    Attributes
    ----------
    name: str
        Name of room.
    ward: hospital.building.ward.Ward
        Ward is parent of the room and can be of any type in
        hospital.building.ward.
    beds: List[hospital.equipment.bed.Bed], optional
        Beds are children of the Room.
    restrictions: List[hospital.restrictions.base.RoomRestrictions], optional
        List of applicable room restrictions.
    """

    aliases = {
        "ward": "parent",
        "beds": "children",
    }

    def __init__(
        self,
        name,
        ward=None,
        beds=None,
        restrictions=None,
    ):
        super(Room, self).__init__()
        self.name = name
        self.parent = ward
        if beds:
            self.children = beds

        self.restrictions = restrictions or []

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

    def __repr__(self):
        cls = self.__class__.__name__
        return f"<{cls}(name={self.name})>"

    @property
    def patients(self):
        return tuple(
            bed.patient for bed in self.beds if bed.patient is not None
        )


class BedBay(Room):
    pass


class SideRoom(Room):
    pass
