import argilla_plugins.active_learning
import argilla_plugins.datasets
import argilla_plugins.inference
import argilla_plugins.programmatic_labelling
import argilla_plugins.reporting
from argilla_plugins.utils.cli_tools import app

__all__ = [
    "active_learning",
    "reporting",
    "datasets",
    "inference",
    "programmatic_labelling",
]

if __name__ == "__main__":
    app()
