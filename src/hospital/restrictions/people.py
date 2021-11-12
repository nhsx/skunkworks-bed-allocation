from hospital.building.room import SideRoom
from hospital.equipment.bed import HighVisibility
from hospital.restrictions.base import PatientRestriction


class NeedsSideRoom(PatientRestriction):
    """
    Patients with immunosuppression or on EoL pathway
    must be admitted to side room.
    """

    def _evaluate_patient(self, patient):
        if patient.bed:
            allocated_room = patient.bed.room
            return (
                self.penalty if not isinstance(allocated_room, SideRoom) else 0
            )
        else:
            return 0


class ProhibitedSideRoom(PatientRestriction):
    """
    Patients with high falls risk can’t be nursed in side rooms.
    """

    def _evaluate_patient(self, patient):
        if patient.bed:
            allocated_room = patient.bed.room
            return self.penalty if isinstance(allocated_room, SideRoom) else 0
        else:
            return 0


class NeedsVisualSupervision(PatientRestriction):
    """
    Patients may require placement in a high visibility bed
    due to behaviour or clinical condition.
    """

    def _evaluate_patient(self, patient):
        if patient.needs_visual_supervision:
            return (
                self.penalty
                if not isinstance(patient.bed, HighVisibility)
                else 0
            )
        else:
            return 0
