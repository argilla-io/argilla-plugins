import logging

import argilla as rg
from argilla import listener

from argilla_plugins.utils.cli_tools import app
from argilla_plugins.utils.dependency_checker import import_package


def template(
    name: str,
    query: str = None,
    *args,  # note that *args and **kwargs are forwarded to the listener
    **kwargs,
):
    """
    __description__

    Args:
        name (str): str, the name of the dataset to which the plugin will be applied.
        query (str): a query string to filter the records that will be deleted.

    Returns:
        __output__
    """
    # import any required packages
    import_package("required_package")

    # define a logger
    log = logging.getLogger(f"template | {name}")

    # potentially add some custom processing logic

    # define a listener https://docs.argilla.io/en/latest/guides/schedule_jobs_with_listeners.html
    @listener(
        dataset=name,
        query=query,
        *args,
        **kwargs,
    )
    def plugin(records, ctx):
        log.info("hello world")

    return plugin
