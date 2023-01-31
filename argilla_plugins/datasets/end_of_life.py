import datetime

import argilla as rg
from argilla import listener

from argilla_plugins.utils.cli_tools import app


@app.command()
def end_of_life(
    name: str = None,
    query: str = None,
    end_of_life_in_seconds: int = None,
    discard_only: bool = False,
    *args,
    **kwargs,
):
    """
    It creates a listener that deletes records from a dataset that are older than a certain time

    Args:
      name (str): str = None,
      query (str): a query string to filter the records that will be deleted.
      end_of_life_in_seconds (int): the number of seconds after which the data will be deleted.
      discard_only (bool): if True, the records will be marked as deleted, but not actually deleted.
    Defaults to False

    Returns:
      A function that takes in records and ctx and deletes the records.
    """
    if end_of_life_in_seconds is None:
        raise ValueError("Provide a `end_of_life_in_seconds`")

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

    query = " AND ".join(query_parts)

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
        rg.delete_records(
            name=ctx.__listener__.dataset, ids=ids, discard_only=discard_only
        )

        # update datetime filter
        if ctx.query_params["end_of_life_date_seconds"]:
            ctx.query_params[
                "end_of_life_date_seconds"
            ] = get_end_of_life_from_seconds()

    print(f"created an end_of_life listener with {query}")

    return plugin
