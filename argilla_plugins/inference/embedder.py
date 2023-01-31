import logging

import argilla as rg
from argilla import listener

from argilla_plugins.utils.dependency_checker import import_package


def embedder(
    name: str,
    query: str = None,
    vector_name: str = "vector",
    model: str = "all-MiniLM-L6-v2",
    device="cpu",
    batch_size=32,
    chunk_size=1000,
    *args,
    **kwargs,
):
    log = logging.getLogger(f"embedder | {name}")
    import_package("sentence_transformers")
    try:
        from fast_sentence_transformers import (
            FastSentenceTransformer as SentenceTransformer,
        )

        sentence_transformer = SentenceTransformer(model, quantize=True, device=device)
    except Exception:
        log.info(
            "Using `sentence-transformers`, try installing `fast_sentence_transformers`"
            " for faster inference."
        )
        from sentence_transformers import SentenceTransformer

        sentence_transformer = SentenceTransformer(model, device=device)

    if query is None:
        query = f"NOT vectors.{vector_name}: *"
    else:
        query = f"({query}) AND NOT vectors.{vector_name}: *"

    @listener(
        dataset=name,
        query=query,
        *args,
        **kwargs,
    )
    def plugin(records, ctx):
        record_chunks = [
            records[i : i + chunk_size] for i in range(0, len(records), chunk_size)
        ]
        for chunk in record_chunks:
            texts = [record.text for record in chunk]
            embeddings = sentence_transformer.encode(texts, batch_size=batch_size)
            for record, vector in zip(chunk, embeddings):
                if record.vectors is None:
                    record.vectors = {}
                record.vectors[vector_name] = [float(num) for num in vector.tolist()]
            log.info(f"logging {len(chunk)} records")
            rg.log(chunk, name=ctx.__listener__.dataset)

    return plugin
