import logging
from collections import Counter

import argilla as rg
from argilla import listener

from argilla_plugins.utils.dependency_checker import import_package


def classy_learner(
    name: str,
    query: str = None,
    model: str = "all-MiniLM-L6-v2",
    classy_config: dict = None,
    certainty_threshold: float = 0,
    overwrite_predictions: bool = True,
    sample_strategy="fifo",
    min_n_samples: int = 6,
    max_n_samples=20,
    batch_size=1000,
    *args,
    **kwargs,
):
    """
    This plugin uses the `classy-classification` package to train a model on a dataset using an active learning loop.

    Args:
        name (str): str, the name of the dataset to which the plugin will be applied.
        query (str): a query string to filter the records that will be considered for updating .
        model (str): The sentence-transformers model to use for inference. Defaults to "all-MiniLM-L6-v2".
        classy_config (dict): A dictionary of configuration parameters for the `classy-classification` package.
        certainty_threshold (float): The minimum certainty threshold for a prediction to be considered correct. Defaults to 0.
        overwrite_predictions (bool): If True, the predictions will be overwritten. Defaults to True.
        sample_strategy (str, optional): Methods for organizing training data samples.
            "fifo" - first in first out for using the most recent data.
            "lifo" - last in first out for using the earliest annotated data.
            Defaults to "fifo".
        min_n_samples (int, optional): Minimum number of data samples per class to start inference. Defaults to 6.
        max_n_samples (int, optional): Maximum nunmber of data samples per class to use during inference. Defaults to 20.
    """
    import_package("classy_classification")
    log = logging.getLogger(f"classy_learner | {name}")
    from classy_classification import ClassyClassifier

    assert min_n_samples > 0, ValueError("`min_n_samples` must be positive")
    assert max_n_samples > 0, ValueError("`max_n_samples` must be positive")
    assert min_n_samples <= max_n_samples, ValueError(
        "`min_n_samples` must be less than or equal to `max_n_samples`"
    )
    assert sample_strategy in ["fifo", "lifo"], ValueError(
        "`sample_strategy` must be either 'fifo' or 'lifo'"
    )
    assert certainty_threshold >= 0 and certainty_threshold <= 1, ValueError(
        "`certainty_threshold` must be between 0 and 1"
    )

    if query is None:
        query = "NOT annotated_as: *"
    else:
        query = f"({query}) AND NOT annotated_as: *"

    @listener(
        dataset=name,
        query="annotated_as: *",
        *args,
        **kwargs,
        data={},
        classy_classifier=None,
        _idx=0,
    )
    def plugin(records, ctx):
        if records:
            # sort records by event_timestamp
            if sample_strategy == "fifo":
                records = sorted(records, key=lambda x: x.event_timestamp)
            elif sample_strategy == "lifo":
                records = sorted(records, key=lambda x: x.event_timestamp, reverse=True)

            # prepare data for classy-classification
            if records[0].multi_label:
                annotations = [
                    [annotation for annotation in rec.annotation] for rec in records
                ]
                texts = [[rec.text for _ in rec.annotation] for rec in records]
                multi_label = True
            else:
                annotations = [rec.annotation for rec in records]
                texts = [rec.text for rec in records]
                multi_label = False

            # check all values in counter are larger than min_n_samples
            counter = dict(Counter(annotations))
            if all([v >= min_n_samples for v in counter.values()]):
                # format data for classy-classification
                data = dict.fromkeys(counter.keys(), [])
                for key, value in zip(annotations, texts):
                    if len(data[key]) <= max_n_samples:
                        data[key].append(value)

                # re-initialize classifier if there is new data
                if ctx.query_params["data"] == data:
                    classy_classifier = ctx.query_params["classy_classifier"]
                else:
                    if ctx.query_params["classy_classifier"] is None:
                        classy_classifier = ClassyClassifier(
                            model=model,
                            data=data,
                            multi_label=multi_label,
                            config=classy_config,
                            verbose=True,
                        )
                    else:
                        # update version _idx when new data is added
                        ctx.query_params["_idx"] = ctx.query_params["_idx"] + 1
                        classy_classifier = ctx.query_params["classy_classifier"]
                        classy_classifier.set_training_data(data=data)

                ctx.query_params["data"] = data
                ctx.query_params["classy_classifier"] = classy_classifier

                relevant_batch_query = (
                    f"({query}) AND ((metadata._idx:"
                    f" {ctx.query_params['_idx']}) OR (NOT"
                    " metadata._idx: *))"
                )
                records = rg.load(
                    name=ctx.__listener__.dataset,
                    query=relevant_batch_query,
                    limit=batch_size,
                )

                if records:
                    updated_records = []
                    texts = [rec.text for rec in records]
                    predictions = classy_classifier.pipe(texts)
                    for rec, pred in zip(records, predictions):
                        max_new_pred = pred[max(pred, key=pred.get)]
                        max_old_pred = 0

                        # format as list of tuples expected by Argilla
                        pred = [(k, v) for k, v in pred.items()]

                        # only overwrite if allowed
                        if rec.prediction and overwrite_predictions:
                            max_old_pred = dict(rec.prediction)[
                                max(dict(rec.prediction), key=dict(rec.prediction).get)
                            ]
                            if (
                                max_new_pred > certainty_threshold
                            ) and (  # pred is certain enough
                                max_new_pred > max_old_pred
                            ):  # new pred is more certain than previous
                                rec.prediction = pred
                                updated_records.append(rec)
                        else:
                            # only add prediction if it is certain enough
                            if max_new_pred > certainty_threshold:
                                # Logging the records to the dataset.
                                rec.prediction = pred
                                updated_records.append(rec)

                    # update _idx for record
                    for rec in updated_records:
                        rec.metadata["_idx"] = ctx.query_params["_idx"]

                    # log data for updated records
                    if updated_records:
                        rg.log(records, name=ctx.__listener__.dataset)
                else:
                    log.info("No records to annotate")
            else:
                log.info(f"Not enough samples to train model. {counter}")
        else:
            log.info("waiting for annotations")

    log.info(f"created an classy_learner listener with {query}")

    return plugin
