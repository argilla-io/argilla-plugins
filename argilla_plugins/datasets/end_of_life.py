import datetime
from typing import Any

import argilla as rg
from argilla import listener


def end_of_life(
    name: str,
    end_of_life_in_seconds: int = None,
    end_of_life_in_datetime: datetime.datetime = None,
    query: str = None,
    execution_interval_in_seconds: int = None,
    condition: Any = None,
):
    """
    It deletes records from a dataset using a listener as background process

    :param name: (str) The name of the dataset to be deleted
    :param end_of_life_in_seconds: (int) The number of seconds after which the records will be deleted
    :param end_of_life_in_datetime: (int) The datetime when the records should be deleted
    :param query: (str) A query to filter the records that will be deleted
    :param execution_interval_in_seconds: (int) The interval at which the plugin will be executed
    :param condition: (Any) A function that takes in a record and returns a boolean. If the function returns
    True, the record will be deleted

    :return: A function that takes in records and ctx and deletes the records.
    """
    if not any([end_of_life_in_seconds, end_of_life_in_datetime]):
        raise ValueError(
            "Provide at least one of the following variables `end_of_life_in_seconds`"
            " and `end_of_life_in_date`"
        )

    if end_of_life_in_seconds:
        assert end_of_life_in_seconds > 0, ValueError(
            "`end_of_life_in_seconds` must be positive"
        )

    que

    @listener(
        dataset=name,
        query=query,
        execution_interval_in_seconds=execution_interval_in_seconds,
        condition=condition,
    )
    def plugin(records, ctx):
        rg.delete_records(records)

    return plugin
