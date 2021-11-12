import copy
import math
import statistics
from itertools import permutations

from anytree import NodeMixin

from agent.policy import random_allocate
from agent.simulator import Simulator, discharge_patients, increment_timers


class Node(NodeMixin):
    """
    Node class used for Monte Carlo Tree Search algorithm.

    Attributes
    ----------
    hospital: hospital.building.building.Hospital
        Hospital structure with wards, rooms beds and patients.
    prior: float
        Prior on UCB value of the node.
    visit_values: List[float]
        Rewards associated with each visit of the node during the tree search.
    immediate_reward: float
        Immediate reward associated with the node action.
    discount_factor: float
        Weighting for future timesteps in the visit value. Discount
        factor ranges between zero and one, where one indicates future moves
        are equaly important and  0 is equivalent to the immediate reward.
    max_tree_depth: int
        Maximum tree depth to expand to. This should be equal to the forecast
        window of the future arrivals.
    action: dict
        Set of bed allocations for t=1 represented by the node.
    """

    def __init__(
        self, hospital, prior, max_tree_depth, discount_factor=0.9, action=None
    ):
        self.hospital = hospital
        self.prior = prior
        self.visit_values = []
        self.immediate_reward = 1 - self.hospital.eval_restrictions()["score"]
        self.discount_factor = discount_factor
        self.max_tree_depth = max_tree_depth
        self.action = action

    @property
    def visit_count(self):
        return len(self.visit_values)

    @property
    def value(self):
        try:
            return statistics.mean(self.visit_values)
        except statistics.StatisticsError:
            return 0

    def is_expandable(self):
        return not self.children

    def attach_child(self, node):
        self.children = self.children + (node,)

    # --- MCTS:
    def select(self):
        node = self
        while not node.is_expandable():
            node = max(node.children, key=ucb_score)
        return node

    def expand(self, patients):
        # TODO add expande behaviour for leaf node when forecast is finished
        # e.g., if node.is_leaf: node.backpropagate([], []) else:
        if not self.is_expandable():
            return

        hospital_copy = copy.deepcopy(self.hospital)
        if not self.is_root:
            increment_timers(hospital_copy)
            discharge_patients(hospital_copy)

        possible_allocations = _allocation_combinations(
            hospital_copy, patients
        )
        if not possible_allocations:
            # TODO add no empty beds action with high penalty
            print("Hospital full, cannot allocate patients")
            return

        num_allocations = len(possible_allocations)
        for combination in possible_allocations:
            new_hospital = copy.deepcopy(hospital_copy)

            for bed_name, patient in combination:
                new_hospital.admit(patient, bed_name)

            child_node = Node(
                new_hospital,
                prior=1 / num_allocations,
                action=dict(combination),
                max_tree_depth=self.max_tree_depth,
                discount_factor=self.discount_factor,
            )
            self.attach_child(child_node)

    def simulate(self, arrival_simulator):
        simulator = Simulator(
            self.hospital, arrival_simulator, random_allocate
        )
        depth = self.max_tree_depth - self.depth
        timesteps = range(depth)
        penalties = simulator.run(depth, progress_bar=False)
        rewards = [1 - p for p in penalties]
        discounts = [self.discount_factor ** t for t in timesteps]
        return rewards, discounts

    def backpropagate(self, rewards, discounts):
        """
        Value: L = R_1 + γ R_2 + ...
        """
        gamma = self.discount_factor
        for node in self.iter_path_reverse():
            rewards = [
                node.immediate_reward,
            ] + rewards
            discounts = [
                1,
            ] + [gamma * d for d in discounts]
            long_term = sum(r * d for r, d in zip(rewards, discounts))
            normalisation = sum(discounts)
            node.visit_values.append(long_term / normalisation)

    def __repr__(self):
        return (
            f"{self.action} -- Value: {self.value}, Count: {self.visit_count}"
        )


def ucb_score(node):
    """
    The score for an action that would transition between the parent and child.
    """
    if node.is_root:
        raise ValueError("Cannot compute UCB score for a root node.")

    ratio = math.sqrt(node.parent.visit_count) / (node.visit_count + 1)
    prior_score = node.prior * ratio
    return node.value + prior_score


def _allocation_combinations(hospital, arrivals_t):
    """
    Returns possible combinations of patients to beds for a given time step.
    """
    empty_beds = hospital.get_empty_beds()
    empty_beds = [bed.name for bed in empty_beds]
    if len(empty_beds) >= len(arrivals_t):
        combinations = [
            list(zip(x, arrivals_t))
            for x in permutations(
                empty_beds,
                len(arrivals_t),
            )
        ]
        return combinations
    else:
        combinations = [
            list(zip(empty_beds, x))
            for x in permutations(
                arrivals_t,
                len(empty_beds),
            )
        ]
        return combinations
