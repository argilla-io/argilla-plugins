from argilla_plugins.datasets import remove_duplicate

plugin = remove_duplicate(
    name="gutenberg_spacy-ner-monitoring",
    query=None,
    discard_only=True,
)
plugin.start()
