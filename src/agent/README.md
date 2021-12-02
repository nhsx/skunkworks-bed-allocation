# Agent Allocation

## Introduction

Once a virtual hospital has been created and populated, we can allocate incoming patients to the best bed. 

There are two approaches to allocating patients to beds provided in this repository:

Approach|Description|Notebook
---|---|---
Greedy|Simple approach which allocates best possible bed for an individual patient at the point of entry, and does not take into account forecasts of future arrivals|[`2.Greedy_Allocation.ipynb`](../../notebooks/2.Greedy_Allocation.ipynb)
Monte Carlo Tree Search (MCTS)|Tree based approach which combines a forecast of upcoming arrivals based on historical data (depth of tree), along with constraints of a patient, and selects the best possible bed (width of tree)|[`3.MCTS_Allocation.ipynb`](../../notebooks/3.MCTS_Allocation.ipynb)

## 1. Greedy Allocation

Greedy optimisation finds the best allocation currently available given the state of the hospital and attributes of the patient. Consider the following example:
<ul>
<li>A female adult medical patient has arrived at the hospital and there are only two available beds. The first is within a bed bay of the male medical ward, the second is within a bed bay of a female surgical ward.
<li>According to user research the penalty for assigning a patient to ward with incorrect sex is 10 whilst the penalty for assigning a medical patient to a surgical ward is 3. 
<li>The greedy algorithm would choose the second bed, finding the solution that incurs the lowest penalty.
</ul>

In a more complicated scenario, where multiple penalties of varying cost may apply, it will optimise for the lowest aggregated penalty, which is a balance between the number of constraints broken and the magnitude of their costs i.e., breaking 1 constraint at a cost of 10 is worse than breaking 2 with a total cost of 7. 

This approach is called ‘greedy’ as it performs a brute force search across all available options. This may be slow if the size of your search space (e.g. number of possible choices) is very large.

We will demonstrate how to run the greedy allocation agent on the hospital that was created from the [hospital](../hospital/README.md) component.

This walkthrough is also available as a [notebook](../../notebooks/2.Greedy_Allocation.ipynb).

### 1.1 Import required modules

```python
import copy
import time
import cloudpickle
import pandas as pd

from agent import policy
from hospital.people import Patient
```

### 1.2 Load the Hospital Environment

We load the saved hospital environment, generated previously, and initialise it with a random set of patients at an occupancy of 90%. After populating the hospital you can see that there are patients attached to 90% of the beds, and also use the hospital functions to get a list of empty bed, understand the current penalty associated with the hospital (N.B. this will be very high as we randomly initialised the hospital).

```python
with open("../data/hospital.pkl", "rb") as f:
        h = cloudpickle.load(f)
```

```python
policy.populate_hospital(h, occupancy=0.9)
h.render()
```

```python
# function returns a generator so wrap in list to see all empty beds
len(list(h.get_empty_beds()))
```

```python
start_penalty = h.eval_restrictions()["score"]
print(f"Start penalty of the hospital: {start_penalty}")
```

### 1.3 Create a patient and Allocate

We can create a patient to allocate and use the `greedy_suggestions` function to return the top N bed suggestions for this patient, given the current state of the hospital. The suggestions are returned as a distionary with the bed names as keys and a dictionary of penalties and violated restrictions as values. Below we unpack this into a pandas DataFrame for easy comparison. 

The greedy allocation agent is plugged into the UI, please refer to the UI to see how this type of tool may be utilised by end users. 

```python
patient = Patient(
    name="patient",
    sex="female",
    department="medicine",
    specialty="general",
    is_immunosupressed=True,
)
```

```python
numer_of_suggestions = 5
start_time = time.time()
suggestions = policy.greedy_suggestions(h, patient, numer_of_suggestions)
elapsed = time.time() - start_time
```

```python
print(f"Time take to compute top {numer_of_suggestions} greedy suggestions: {round(elapsed,2)}s")

df = pd.DataFrame(suggestions).T
df
```

## 2. Monte Carlo Tree Search (MCTS)

A full review of MCTS is available in [Browne et al., 2012](http://ccg.doc.gold.ac.uk/ccg_old/papers/browne_tciaig12_1.pdf), and has been the basis of the below work.

Broadly speaking MCTS randomly explores a decision space, building a tree of connected moves and their associated rewards. Over multiple iterations the MCTS determines which decisions are most likely to result in a positive outcome. Ultimately the best decision is the one that provides the best long term reward, the definition of which depends on the specific domain. For example, when creating a MCTS agent to play a board game, the long term reward would be a 0 or 1 depending on whether you won or lost the game after making the current move. 

In the context of bed allocation we do not have a natural end state. Therefore the long term reward is determined as the total reward incurred after N time has passed according to the equation below. Here <img src="https://render.githubusercontent.com/render/math?math=\color{white}R_{n}#gh-dark-mode-only"><img src="https://render.githubusercontent.com/render/math?math=\color{black}R_{n}#gh-light-mode-only"> represents a reward associated with  the state of the hospital at a given time step, <img src="https://render.githubusercontent.com/render/math?math=\color{white}\gamma \epsilon [0, 1]#gh-dark-mode-only"><img src="https://render.githubusercontent.com/render/math?math=\color{black}\gamma \epsilon [0, 1]#gh-light-mode-only"> is the discount factor. The reward associated with a hospital state is <img src="https://render.githubusercontent.com/render/math?math=\color{white}1 - total penalties#gh-dark-mode-only"><img src="https://render.githubusercontent.com/render/math?math=\color{black}1 - total penalties#gh-light-mode-only"> incurred. The first term in the equation, <img src="https://render.githubusercontent.com/render/math?math=\color{white}R_{1}#gh-dark-mode-only"><img src="https://render.githubusercontent.com/render/math?math=\color{black}R_{1}#gh-light-mode-only">, is the immediate reward associated with the current allocation i.e., the greedy allocation score, and the subsequent terms are rewards associated with future states, where the discount factor weighs the relative importance of these future states against the current state. 

<img src="https://render.githubusercontent.com/render/math?math=\color{white}R = R_{1} + \gamma R_{2} +\gamma^{2}R_{3} ... +\gamma^{N}R_{N}#gh-dark-mode-only"><img src="https://render.githubusercontent.com/render/math?math=\color{black}R = R_{1} + \gamma R_{2} +\gamma^{2}R_{3} ... +\gamma^{N}R_{N}#gh-light-mode-only">

In this walkthrough we demonstrate how to run the MCTS allocation algorithm in the virtual hospital; see [`src/agent/mcts`](mcts/) and [`src/agent/simulation`](simulation) for the relevant code.

This walkthrough is also available as a [notebook](../../notebooks/3.MCTS_Allocation.ipynb).

### 2.1 Import required modules

```python
import cloudpickle
import copy
import time

import warnings
warnings.filterwarnings('ignore')

import agent.utils as utils
import agent.policy as policy
import agent.run_mcts as mcts
from hospital.people import Patient
from forecasting.patient_sampler import PatientSampler
```

### 2.2 Load the Hospital Environment

We load the saved hospital environment and initialise it with a random set of patients at an occupancy of 90% and normalise the restriction penalties to lie between 0-1.

```python
with open("../data/hospital.pkl", "rb") as f:
        h = cloudpickle.load(f)
        
policy.populate_hospital(h, occupancy=0.90)
h.render()
```

```python
len(list(h.get_empty_beds()))
```

```python
# you will also need to normalise the penalties to lie between 0 and 1
utils.normalise_ward_penalties(h)
```

### 2.3 Create patients to admit to the hospital

We first create the Patient we currently want to allocate like we did in the first notebook. Then we use the patient sampler to generate the arrivals forecast used to simulate the future within the MCTS. 

We use the PatientSampler class to provide a list of incoming patients as below. The sampler takes a day of week and an hour of the day and returns a forecast for the number of patients estimated to arrive each hour, `N`. By default, the patients are synthesied with random data where the distribution for each attributes is informed by aggregated historic data. If historic patient data is available then a pool of historic patients can be saved and setting `historic=True` will return more accurate marginal distributions accross all patient attributes. The function call and outputs are otherwise the same, but at the moment the returned number of patients `N` is a random number, and the returned patients are randomly generated. See [`src/forecasting/patient_sampler`](../forecasting/patient_sampler). 

```python
patient = Patient(
    name="patient",
    sex="female",
    department="medicine",
    specialty="general",
    is_known_covid=True,
)
```

```python
sampler = PatientSampler("monday", 9)
forcast_window=2
forecasted_patients = sampler.sample_patients(forecast_window=forcast_window, num_samples=1)

# we can unpack the above structure into a list of lists
# each sublist represents an hour of patients
arrivals = []
for _, patients in forecasted_patients[0].items():
    arrivals.append(patients)
    
print(f"Incoming patients per hour: {[len(l) for l in arrivals]}")
```

now we insert the patient we are currently trying to allocate as the first patient, as time t=1.

```python
arrivals = [[patient]] + arrivals
arrivals
```

**WARNING: This following code may take a long time or cause memory issues if a lot of patients (>4) are arriving in a single time step or the forecast window is large (>2)**

```python
h_copy = copy.deepcopy(h)
t = time.time()
mcts_node = mcts.run_mcts(
        h_copy,
        arrivals,
        discount_factor=0.9,
        n_iterations=10,
)
elapsed = time.time() - t
mcts_output = mcts.construct_mcts_output(h_copy, mcts_node, patient)
```

```python
print(f"Time taken to compute suggestions: {round(elapsed,2)}s")
mcts_output
```

### 2.4 Details on implementation

Below we describe the four stages of the MCTS algorithm as they are specifically implemented for the bed allocation agent. The implementation utilises the `anytree` library to build a tree structure, where each node represents a specific state of the hospital and each level of the tree represents a time step. Time steps are incremented in hours and connected to the number of forecasted admissions arriving each hour. The input to the treesearch is a queue of patients arriving at each time step, with the current patient to be allocated (`t=0`) as the first entry in this queue, and the current state of the hospital as the root node to search from.

<ol>
<li><b>Selection</b></li>

Starting at the root node a child node is selected. The root node represents the current state of the hospital at time <img src="https://render.githubusercontent.com/render/math?math=\color{white}t=0#gh-dark-mode-only"><img src="https://render.githubusercontent.com/render/math?math=\color{black}t=0#gh-light-mode-only"> where the state is defined by the patients that are currently occupying beds and the set of empty beds. 

In the first iteration of the tree search, the algorithm selects the root node and moves to the expansion step. In subsequent iterations it will traverse from the root and choose one of the child nodes according to the tree policy. The <i>tree policy</i> is the UCB score, in which <img src="https://render.githubusercontent.com/render/math?math=\color{white}\overline{R}#gh-dark-mode-only"><img src="https://render.githubusercontent.com/render/math?math=\color{black}\overline{R}#gh-light-mode-only"> is the mean reward from visiting that node, <img src="https://render.githubusercontent.com/render/math?math=\color{white}N_{pi}#gh-dark-mode-only"><img src="https://render.githubusercontent.com/render/math?math=\color{black}N_{pi}#gh-light-mode-only"> is the number of times its parent node was visited and <img src="https://render.githubusercontent.com/render/math?math=\color{white}N_{i}#gh-dark-mode-only"><img src="https://render.githubusercontent.com/render/math?math=\color{black}N_{i}#gh-light-mode-only"> is the number of times the node itself has been visited. The first term encourages the algorithm to select nodes that have previously resulted in good outcomes, while the second encourages the algorithm to explore options that it hasn’t visited as often.

<img src="https://render.githubusercontent.com/render/math?math=\color{white}UCB = \overline{R} + \sqrt{\frac{2 \log{N_{p}}}{N_{i}}}#gh-dark-mode-only"><img src="https://render.githubusercontent.com/render/math?math=\color{black}UCB = \overline{R} + \sqrt{\frac{2 \log{N_{p}}}{N_{i}}}#gh-light-mode-only">

<li><b>Expansion</b></li>
Once a node is selected, a child node is attached to represent each possible decision state for that time step.

For example, we have a hospital with 4 beds, 2 are occupied and 2 are available. We are currently trying to allocate a patient P1. As there are two possible decisions, two nodes can be attached that represent 1) allocating P1 to the first available bed and 2) allocation P1 to the second available bed.

As we progress through the tree search, we may encounter time steps where multiple patients have arrived. In such cases, a node is expanded for each possible combination of patients to available beds.
<li><b>Simulation</b></li>
From one of the attached children we then simulate a future. The simulation stage involves the following steps:
<ul>
<li>Each patient currently within the hospital has a length of stay attribute, and an expected length of stay attribute. At the start of the simulation step, the length of stay counters are incremented by one.</li>
<li>Then a discharge model is applied to discharge existing patients. The probability of being discharged increases according to proximity to your expected length of stay.</li>
<li>The patients arriving in the given time-step are then assigned to beds according to the default policy. The default policy is a random assignment of patients to beds to available beds.</li>
</ul>
<li><b>Backpropagation</b></li>
The total penalty of the hospital is calculated after the simulation step. This is the sum of all penalties for each broken restriction within the hospital. We then backpropagate this score up the tree to distribute the outcome across all decisions along the currently explored path. 

This stage updates the UCB score (tree policy score) and visit count for each node that was traversed along the current decision pathway. If the result of the simulation was good, the UCB scores of each node will have increased, making it more likely that future iterations of the tree search will select these nodes again. The reverse is also true. In this manner MCTS is more tractable than a completely random search of the possible decision pathways as it more frequently visits the most promising options during the selection stage.
</ol>
The above procedure is repeated multiple times until a maximum number of iterations have been reached. At this point the tree object is returned and the best child node of the root is selected as the optimal allocation for the current patient. There are several potential strategies for determining what the best node is. In the current implementation we choose the node that has the highest visit count. Alternative approaches such as choosing the node with the highest UCB score or some balance of the two, and how this affects outcomes, remain to be explored in future work.

### Limitations
In the above implementation we take a single sample from the demand forecast and use this as a fixed version of the future. This means that the future within the treesearch is deterministic and significantly reduces the search space, and branching of the tree, allowing the algorithm to find a recommendation in a more tractable timeframe. However, a single sample from the forecast represents one of the possible futures. To truly capture the variability of incoming patients, we envisage a strategy where multiple simultaneous tree searches are implemented, each using a separate sample from the forecasted admissions. These could be run in parallel to increase runtime efficiency, and the final suggested allocation would be the bed that has the average highest ranking across the ensemble of tree searches. The efficacy of this strategy and alternative approaches to dealing with non deterministic search spaces remain to be explored. 

Despite fixing the set of arrivals within a tree-search we can still experience an intractable amount of branching that makes the current implementation of MCTS unsuitable for operational use. For example, if there are just 4 empty beds in the hospital, and 9 arriving patients within a time step, the tree expands into 840 possible permutations of patients to beds. With multiple time steps into the future this can compound and result in either memory issues or extremely long compute times. Further work is needed to explore engineering strategies that can make MCTS more operationally feasible.