import argilla_plugins.inference
import argilla_plugins.programmatic_labelling
import argilla_plugins.reporting
from argilla_plugins.active_learning import *
from argilla_plugins.datasets import *
from argilla_plugins.utils.cli_tools import app

app.command(end_of_life)


__all__ = [
    "end_of_life",
    "classy_learner",
    "datasets",
    "inference",
    "programmatic_labelling",
]

if __name__ == "__main__":
    app()
