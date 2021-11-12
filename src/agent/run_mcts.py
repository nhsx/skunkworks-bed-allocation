from agent.mcts import Node
from agent.utils import arrivals_generator, reduce_restrictions


def run_mcts(
    hospital,
    arrivals,
    discount_factor=0.9,
    n_iterations=100,
):
    """
    Runs the MCTS algorithm from an initialised hospital state.

    Parameters
    ----------
    hospital: hospital.building.Hospital
        Initial state of the hospital.
    arrivals: List[List[Patient(...), Patient(...)]]
        Nested list of forecasted arrivals where each sublist represents
        a single time step (hour) of incoming patients. The first entry should
        be a contain the patient(s) that are currently being allocated.
    discount_factor: float
        Weight between 0-1 to tune how important future steps are in the final
        allocation.
    n_iterations: int
        Number of iterations to perform before terminating the search.
    max_treedepth: int
        number of timesteps into the future through which to search.

    Returns
    -------
    root: agent.mcts.Node
        MCTS Node object who's children represent the possible allocations for
        the current patient(s). Properties, visit_count, and value can be used
        to determine the best allocation.
    """
    max_tree_depth = len(arrivals)
    root = Node(
        hospital,
        prior=0,
        max_tree_depth=max_tree_depth,
        discount_factor=discount_factor,
    )
    for _ in range(n_iterations):
        node = root.select()
        if node.depth >= max_tree_depth:
            # cannot expand the past the length of the arrivals forecast
            pass
        else:
            node.expand(arrivals[node.depth])
            print(
                f"Empty beds: {len(list(node.hospital.get_empty_beds()))}, ",
                f"arrivals: {len(arrivals[node.depth])}",
            )
            for child in node.children:
                if child.depth >= max_tree_depth:
                    pass
                else:
                    rewards, discounts = child.simulate(
                        arrival_simulator=arrivals_generator(
                            arrivals[child.depth]
                        ),
                    )
                    child.backpropagate(rewards, discounts)

    return root


def construct_mcts_output(hospital, root_node, patient):
    """
    Returns an ordered dictionary of the allocation scores and violated
    restrictions for each potential allocation of the patient.

    Keys are ordered by the number of visit counts during the tree search,
    in descending order, such that the first item is the best allocation.
    """

    base_state = hospital.eval_restrictions()

    allocation_scores = []
    for child in root_node.children:
        admitted_patients = []
        for bed_name, patient in child.action.items():
            admitted_patients.append(patient)
            hospital.admit(patient, bed_name)

        hospital_eval = hospital.eval_restrictions()
        allocation_scores.append(
            {
                "action": child.action,
                "score": hospital_eval["score"] - base_state["score"],
                "violated_restrictions": reduce_restrictions(
                    base_state["names"], hospital_eval["names"]
                ),
                "ucb_score": child.value,
                "visit_count": child.visit_count,
            }
        )
        for patient in admitted_patients:
            hospital.discharge(patient)

    return allocation_scores
