import logging

from rich.logging import RichHandler

from argilla_plugins.active_learning import *
from argilla_plugins.datasets import *
from argilla_plugins.inference import *
from argilla_plugins.programmatic_labelling import *
from argilla_plugins.reporting import *
from argilla_plugins.utils.cli_tools import app

app.command(end_of_life)


__all__ = [
    "end_of_life",
    "classy_learner",
    "token_copycat",
    "inference",
    "programmatic_labelling",
]


FORMAT = "%(name)s | %(message)s"
logging.basicConfig(
    level="INFO",
    format=FORMAT,
    datefmt="[%X]",
    handlers=[RichHandler(rich_tracebacks=True)],
)


if __name__ == "__main__":
    app()
