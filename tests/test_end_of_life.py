from argilla_plugins.datasets import end_of_life

plugin = end_of_life(
    name="plugin-test",
    end_of_life_in_seconds=100,
    execution_interval_in_seconds=5,
)
plugin.start()
