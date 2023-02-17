import argilla as ar
from argilla_plugins.datasets import remove_duplicate

"""
requires an ElasticSearch instance running at localhost:9200
"""
def test_remove_duplicate(mocked_client):
    ds_name = "test-dataset"

    # Let's generate records from those words.
    # 1 with egg, 2 with potato, 3 with onion.
    # After applying the listener,
    # we should end up with only three records
    content = [
        "Egg",
        "Potato",
        "Onion"
    ]
    records = list()
    id_count = 0
    for word_position, word in enumerate(content):
        for _ in range(word_position + 1):
            record = ar.TextClassificationRecord(
                id=id_count,
                text=word,
                prediction=[("ok", 1)],
            )
            id_count += 1
            records.append(record)
    assert len(records) == 6
    ar.log(records=records, name=ds_name)

    import logging
    l = logging.getLogger(f"remove_duplicate | {ds_name}")
    l.setLevel(logging.DEBUG)

    listener = remove_duplicate(ds_name)
    ctx = ar.RGListenerContext(listener)
    listener.action(records, ctx)

    number_active_records = 0
    unique_content = set()
    for rec in ar.load(ds_name):
        print(f"res: {rec.id} - {rec.text} - {rec.status}")
        if rec.status == "Default":
            number_active_records += 1
            unique_content.add(rec.text)
    assert len(unique_content) == 3
    assert number_active_records == 3

    # ds = ar.DatasetForTextClassification(
    #     records=records,
    # )
    #
    # listener = remove_duplicate(
    #     ds_name,
    #     execution_interval_in_seconds=1
    # )
    # listener.start()
    # listener.stop()
    #
    # # import pdb
    # # pdb.set_trace()
    #
    # number_active_records = 0
    # unique_content = set()
    # for rec in ds:
    #     print(f"res: {rec.text} - {rec.status}")
    #     if rec.status == "Default":
    #         number_active_records += 1
    #         unique_content.add(rec.text)
    # assert len(unique_content) == 3
    # assert number_active_records == 3

    assert False


