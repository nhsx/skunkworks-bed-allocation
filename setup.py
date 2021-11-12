"""Setup file for kgh.

Please note that setup.cfg is used for configuration.
"""
from setuptools import setup

if __name__ == "__main__":
    setup(
        use_scm_version=True,
        python_requires=">3.5",
    )
