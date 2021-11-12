from hospital.building.room import SideRoom
from hospital.data import Department
from hospital.restrictions.base import WardRestriction


class NoAcuteSurgical(WardRestriction):
    """
    No acute surgical patients admitted
    """

    def _evaluate_bed(self, bed):
        is_acute_surgical = getattr(bed.patient, "is_acute_surgical", False)
        return self.penalty if is_acute_surgical else 0


class NoKnownCovid(WardRestriction):
    """
    Do not admit patients who are known to have covid, except into
    side rooms.
    """

    def _evaluate_bed(self, bed):
        known_covid = getattr(bed.patient, "is_known_covid", False)
        if isinstance(bed.room, SideRoom):
            return 0
        else:
            return self.penalty if known_covid else 0


class NoSuspectedCovid(WardRestriction):
    """
    Do not admit patients who are suspected to have covid, except into
    side rooms.
    """

    def _evaluate_bed(self, bed):
        suspected_covid = getattr(bed.patient, "is_suspected_covid", False)
        if isinstance(bed.room, SideRoom):
            return 0
        else:
            return self.penalty if suspected_covid else 0


class NoNonCovid(WardRestriction):
    """
    Do not admit patients who are not known or suspected to have covid except
    into side rooms.
    """

    def _evaluate_bed(self, bed):
        if isinstance(bed.room, SideRoom):
            return 0
        elif bed.patient:
            known_covid = getattr(bed.patient, "is_known_covid", False)
            suspected_covid = getattr(bed.patient, "is_suspected_covid", False)
            return 0 if known_covid or suspected_covid else self.penalty
        else:
            return 0


class NoPatientsOver100kg(WardRestriction):
    """
    Do not admit patients that weight over 100kg
    """

    def _evaluate_bed(self, bed):
        patient_weight = getattr(bed.patient, "weight", 70.0)
        return self.penalty if patient_weight > 100.0 else 0


class IncorrectSex(WardRestriction):
    """
    Only admit patients who match the ward sex.
    """

    def _evaluate_bed(self, bed):
        ward_sex = bed.room.ward.sex
        patient_sex = getattr(bed.patient, "sex", ward_sex)
        return self.penalty if patient_sex.value != ward_sex.value else 0


class NoMobilityAssistance(WardRestriction):
    """
    Do not admit patients that are not independently mobile
    or cannot transfer without an aid.
    """

    def _evaluate_bed(self, bed):
        needs_assistence = getattr(
            bed.patient, "needs_mobility_assistence", False
        )
        return self.penalty if needs_assistence else 0


class NoDementiaRisk(WardRestriction):
    """
    Do not admit patients that are confused or at risk of wandering.
    """

    def _evaluate_bed(self, bed):
        dementia_risk = getattr(bed.patient, "is_dementia_risk", False)
        return self.penalty if dementia_risk else 0


class NoHighAcuity(WardRestriction):
    """
    Do not admit high acuity patients.
    """

    def _evaluate_bed(self, bed):
        high_acuity = getattr(bed.patient, "is_high_acuity", False)
        return self.penalty if high_acuity else 0


class NoNonElective(WardRestriction):
    """
    Do not admit non-elective patients.
    """

    def _evaluate_bed(self, bed):
        if bed.patient:
            elective = getattr(bed.patient, "is_elective", False)
            return 0 if elective else self.penalty
        else:
            return 0


class NoSurgical(WardRestriction):
    """
    Do not admit surgical patients.
    """

    def _evaluate_bed(self, bed):
        if bed.patient:
            department = bed.patient.department
            return (
                self.penalty
                if department.value == Department.surgery.value
                else 0
            )
        else:
            return 0


class NoMedical(WardRestriction):
    """
    Do not admit medical patients.
    """

    def _evaluate_bed(self, bed):
        if bed.patient:
            department = bed.patient.department
            return (
                self.penalty
                if department.value == Department.medicine.value
                else 0
            )
        else:
            return 0


class IncorrectSpecialty(WardRestriction):
    """
    Do not assign patient to wards with incorrect specialties.
    """

    def _evaluate_bed(self, bed):
        if bed.patient:
            patient_specialty = bed.patient.specialty
            ward_specialties = bed.room.ward.specialty
            return 0 if patient_specialty in ward_specialties else self.penalty
        else:
            return 0
