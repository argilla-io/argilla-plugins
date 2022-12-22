import datetime

import argilla as rg

from argilla_plugins.datasets import end_of_life

plugin = end_of_life(
    "plugin-test",
    end_of_life_in_seconds=100,
    end_of_life_in_datetime=datetime.datetime.now(),
    execution_interval_in_seconds=5,
)
plugin.start()
