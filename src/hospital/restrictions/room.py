from hospital.restrictions.base import RoomRestriction


class NoMixedSex(RoomRestriction):
    """
    Bed bay must be single sex.
    """

    def _evaluate_room(self, room):
        room_sexes = {
            bed.patient.sex.value
            for bed in room.beds
            if bed.patient is not None
        }
        return self.penalty if len(room_sexes) > 1 else 0


class KeepSideRoomEmpty(RoomRestriction):
    """
    Side room must always be kept empty, e.g., for emergency AGP.
    """

    def _evaluate_room(self, room):
        return 0 if len(room.patients) == 0 else self.penalty
