# KGH Operation

Bed allocation project for KGH.

## Description

This project consists of 4 components:
<ol>
<li> Hospital Simulator
<li> Demand Forecaster
<li> Allocation Agent
<li> UI
</ol>

Components 1-3 form the backend of the bed optimisation framework and can be found within `kgh/src/`.
The UI component is built with Plotly Dash and can be found within `kgh/app/`.

## Installation

This project requires Python 3, If your system is running an older version
of Python we recommend creating a conda environment with Python 3.9 to install
the package.

For standard installation run `pip install .` from within the kgh directory.

To install in dev mode with the [Pytest](https://docs.pytest.org/en/6.2.x/) testing suite available run
````pip install -e ."[testing]"```.
