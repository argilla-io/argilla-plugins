from argilla_plugins import embedder

plugin = embedder(
    name="ray_asgi_transformer",
    query=None,
    vector_name="vector",
    model="all-MiniLM-L6-v2",
    device="cpu",
    batch_size=32,
    chunk_size=1000,
    execution_interval_in_seconds=5,
)
plugin.start()
