import datetime

import argilla as rg

from argilla_plugins.programmatic_labelling import token_classification_copycat

plugin = token_classification_copycat("nlp-summit", execution_interval_in_seconds=1)
plugin.start()
