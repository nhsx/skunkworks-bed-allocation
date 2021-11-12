import copy
import queue

from tqdm import tqdm

from agent.utils import bernoulli, logistic
from hospital.building.building import Hospital


class Simulator:
    """
    Attributes
    ----------
    hospital: Hospital
        An instance of the hospital class.

    generator: Callable -- must return a list of patients on call.
        This function will be called by the simulator to simulate
        a random arrival of patients to the hospital each time
        the function is called.

    policy: An allocation policy function.
        Must accept a hospital and a queue as arguments
        and modify the hospital in-place.
    """

    def __init__(self, hospital, generator, policy):

        self._original_hospital = hospital
        self.hospital = copy.deepcopy(hospital)
        self.generator = generator
        self.queue = queue.Queue()
        self.policy = policy

    def run(self, num_timesteps, progress_bar=True):
        def _do_nothing(x):
            return x

        bar = tqdm if progress_bar else _do_nothing
        return [self.simulate_once() for _ in bar(range(num_timesteps))]

    def simulate_once(self):
        """
        Simulate 1 timestep.
        """
        self.simulate_discharges()
        self.simulate_arrivals()
        self.simulate_allocations()
        return self.hospital.eval_restrictions()["score"]

    def simulate_arrivals(self):
        try:
            self.queue.put(next(self.generator))
        except StopIteration:
            pass

    def simulate_discharges(self):
        increment_timers(self.hospital)
        discharge_patients(self.hospital)

    def simulate_allocations(self):
        self.policy(self.hospital, self.queue)

    def reset(self):
        """
        Restore the original state of the hospital and
        flush the queue of patients.
        """
        self.hospital = copy.deepcopy(self._original_hospital)
        self.queue = queue.Queue()


def increment_timers(hospital: Hospital, timedelta: int = 1):
    """
    Increments the length of stay timers on each patient within a hospital.
    """
    for patient in hospital.patients:
        patient.length_of_stay += timedelta


def discharge_patients(hospital: Hospital):
    """
    Discharges patients that have exceeded their expected length of stay
    """
    for bed in hospital.get_occupied_beds():
        patient = bed.patient
        t = patient.length_of_stay
        T = patient.expected_length_of_stay
        # For testing only, otherwise logistic(2 * (t - T + 1))
        discharge_proba = logistic(2 * (t - T + 1))  # int(t > T)
        is_discharge = bernoulli(discharge_proba)
        if is_discharge:
            bed.vacate()
