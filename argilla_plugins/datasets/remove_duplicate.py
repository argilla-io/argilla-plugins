import logging

import argilla as ar
from argilla import listener

from argilla_plugins.utils.cli_tools import app


@app.command()
def remove_duplicate(
    name: str,
    query: str = None,
    discard_only: bool = False,
    *args,
    **kwargs,
):
    """
    It creates a listener that deletes records from a dataset if their content is similar to other records.

    Args:
      name (str): str, the name of the dataset to which the plugin will be applied.
      query (str): a query string to filter the records that will be deleted.
      discard_only (bool): if True, the records will be marked as deleted, but not actually deleted.
    Defaults to False

    Returns:
      A function that takes in records and ctx and deletes the records.
    """
    log = logging.getLogger(f"remove_duplicate | {name}")

    if query:
        query_parts = [query]
    else:
        query_parts = []

    query = " AND ".join(query_parts)

    @listener(
        dataset=name,
        query=query,
        condition=lambda search: search.total > 2
        *args,
        **kwargs,
    )
    def plugin(records, ctx):
        duplicated_ids = set()
        known_texts = set()
        for rec in records:
            rec_text = rec.text
            if rec_text is not None:
                if rec_text in known_texts:
                    duplicated_ids.add(rec.id)
                else:
                    known_texts.add(rec_text)

        log.debug(f"Found {len(duplicated_ids)} duplicatas")
        log.debug(duplicated_ids)
        if duplicated_ids:
            log.info("deleting %s records", len(duplicated_ids))
            ar.delete_records(
                name=ctx.__listener__.dataset,
                ids=list(duplicated_ids),
                discard_only=discard_only,
            )

    log.info(f"created a remove_duplicate listener with {query}")

    return plugin
