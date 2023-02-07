from argilla_plugins import classy_learner

plugin = classy_learner(
    name="plugin-test",
    query=None,
    model="all-MiniLM-L6-v2",
    classy_config=None,
    certainty_threshold=0,
    overwrite_predictions=True,
    sample_strategy="fifo",
    min_n_samples=6,
    max_n_samples=20,
    batch_size=1000,
    execution_interval_in_seconds=5,
)
plugin.start()
