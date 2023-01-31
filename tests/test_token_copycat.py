from argilla_plugins import token_copycat

plugin = token_copycat(
    name="plugin-test",
    query=None,
    copy_predictions=True,
    word_dict_kb_predictions={"key": {"label": "label", "score": 0}},
    copy_annotations=True,
    word_dict_kb_annotations={"key": {"label": "label", "score": 0}},
    included_labels=["label"],
    case_sensitive=True,
    execution_interval_in_seconds=1,
)
plugin.start()
