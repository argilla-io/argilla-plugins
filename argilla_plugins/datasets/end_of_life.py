import datetime
import warnings
from typing import Any

import argilla as rg
from argilla import listener


def end_of_life(
    name: str = None,
    end_of_life_in_seconds: int = None,
    end_of_life_in_datetime: datetime.datetime = None,
    query: str = None,
    *args,
    **kwargs,
):
    """
    It deletes records from a dataset using a listener as background process

    :param name: (str) The name of the dataset to be deleted
    :param ws: (str) The name of the dataset to be deleted
    :param end_of_life_in_seconds: (int) The variable number of seconds after which records will be deleted
    :param end_of_life_in_datetime: (int) The fixed datetime when the records should be deleted
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

    def get_end_of_life_from_seconds(seconds=end_of_life_in_seconds):
        return (
            datetime.datetime.now() - datetime.timedelta(seconds=seconds)
        ).isoformat()

    if query:
        query_parts = [query]
    else:
        query_parts = []

    # add flexible query parameter end_of_life_date_seconds
    if end_of_life_in_seconds:
        assert isinstance(end_of_life_in_seconds, int), ValueError(
            "`end_of_life_in_seconds`must be an integer"
        )
        assert end_of_life_in_seconds > 0, ValueError(
            "`end_of_life_in_seconds` must be positive"
        )
        start_end_of_life_date_seconds = get_end_of_life_from_seconds()
        query_parts.append("NOT event_timestamp:[{end_of_life_date_seconds} TO *]")

    else:
        start_end_of_life_date_seconds = None

    # add end_of_life_in_datetime filter
    if end_of_life_in_datetime:
        assert isinstance(end_of_life_in_datetime, datetime.datetime), ValueError(
            "`end_of_life_in_seconds`must be an datatime.datetime"
        )
        if end_of_life_in_datetime > datetime.datetime.now():
            warnings.warn("Scheduling data deletion for a moment in the future.")
        query_parts.append(
            f"NOT event_timestamp:[{end_of_life_in_datetime.isoformat()} TO *]"
        )

    query = " AND ".join(query_parts)

    print(f"starting end of lifen listener with {query}")

    @listener(
        dataset=name,
        query=query,
        *args,
        **kwargs,
        end_of_life_date_seconds=start_end_of_life_date_seconds,
    )
    def plugin(records, ctx):
        # delete records
        ids = [rec.id for rec in records]
        rg.delete_records(name=ctx.__listener__.dataset, ids=ids)

        # update datetime filter
        if ctx.query_params["end_of_life_date_seconds"]:
            ctx.query_params[
                "end_of_life_date_seconds"
            ] = get_end_of_life_from_seconds()

    return plugin
