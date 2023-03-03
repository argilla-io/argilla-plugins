import copy
import logging
import re
import string
from typing import Any, Dict, List, Set, Tuple

import argilla as rg
from argilla import listener
from argilla.utils.span_utils import SpanUtils


def token_copycat(
    name: str,
    query: str = None,
    copy_predictions: bool = True,
    word_dict_kb_annotations: dict = None,
    copy_annotations: bool = False,
    word_dict_kb_predictions: dict = None,
    included_labels: list = None,
    case_sensitive: bool = True,
    *args,
    **kwargs,
) -> callable:
    """
    For each record in the dataset, we look at the text and check if there is a word that is in the
    word_dict. If there is, we add the label and the span to the record

    Args:
        name (str): the name of the dataset to which the plugin will be applied.
        query (str): str = None,
        copy_predictions (bool): if True, the predictions from the KB will be copied to the current
        record. Defaults to True
        word_dict_kb_annotations (dict): dict = None, a dictionary of words and their annotations {"key": {"label": "label", "score": 0}}
        copy_annotations (bool): if True, the annotations from the KB will be copied to the record.
        word_dict_kb_predictions (dict): dict = None, a dictionary of words and their predictions {"key": {"label": "label", "score": 0}}
            Defaults to False
        included_labels (list): list = None, a list of labels that will be copied from the KB to the record
        case_sensitive (bool): bool = True, if True, the word_dict matching will be case sensitive. Defaults to True

    Returns:
        A function that takes in a dataset and a context and returns a dataset with the annotations and
        predictions copied from the knowledge base.
    """

    assert any([copy_predictions, copy_annotations]), ValueError(
        "choose to use at least one of the copy_prediction or copy_annotations"
    )
    seen_words = set()
    if word_dict_kb_annotations is None:
        word_dict_kb_annotations = {}
    if word_dict_kb_predictions is None:
        word_dict_kb_predictions = {}

    query_part = []
    if copy_predictions:
        query_part.append("(annotated_as: *)")
    if copy_annotations:
        query_part.append("(predicted_as: *)")
    if query_part:
        query_part = " OR ".join(query_part)

    if query_part and query:
        query = f"{query} AND ({query_part})"
    elif query_part:
        query = query_part

    log = logging.getLogger(f"token_copycat | {name}")

    @listener(
        dataset=name,
        query=query,
        *args,
        **kwargs,
        word_dict_kb_predictions=word_dict_kb_predictions,
        word_dict_kb_annotations=word_dict_kb_annotations,
    )
    def plugin(records, ctx):
        def apply_word_dict_kb(
            rec: Any, word_dict: Dict[str, Dict[str, Any]]
        ) -> List[Tuple[str, int, int, float]]:
            """
            For each know label and known word, get the character span from the text and assign it to the predictions as
            [(label, start, end, 0)]
            """
            util_rec = SpanUtils(rec.text, rec.tokens)
            record_info = []
            for word, word_info in word_dict.items():
                if (
                    included_labels is not None
                    and word_info["label"] not in included_labels
                ):
                    continue

                if case_sensitive:
                    start = [m.start() for m in re.finditer(word, rec.text)]
                else:
                    start = [
                        m.start() for m in re.finditer(word.lower(), rec.text.lower())
                    ]
                for s in start:
                    end = s + len(word)
                    if end < len(rec.text):
                        # check if not alpha
                        if (
                            rec.text[end] not in string.ascii_letters
                        ):  # ensure it is not a subword
                            try:
                                util_rec.validate([(word_info["label"], s, end)])
                                record_info.append(
                                    (word_info["label"], s, end, word_info["score"])
                                )
                            except Exception:
                                pass
            return record_info

        def update_word_dict_kb(
            rec: Any,
            rec_info: List[Tuple[str, int, int, float]],
            word_dict: Dict[str, Dict[str, Any]],
        ) -> Dict[str, Dict[str, Any]]:
            """
            For each prediction, update the word_dict with the word and the label
            """
            for pred in rec_info:
                if len(pred) != 4:
                    label, start, end = pred
                    score = None
                else:
                    label, start, end, score = pred
                if included_labels is not None and label not in included_labels:
                    continue
                word = rec.text[start:end]
                seen_words.add(word)
                word_dict[word] = {"label": label, "score": score}
            return word_dict

        def resolve_span_overlap(
            record_info: List[Tuple[str, int, int, float]]
        ) -> List[Tuple[str, int, int, float]]:
            """
            Spans are provided as a list of tuples [(label, start, end, score)].
            This list is sorted by start index.
            Then this function checks if there is an overlap between the spans.
            The longest span is kept and the other is removed.
            """
            def get_sort_key(record_info):
                return record_info[2] - record_info[1], -record_info[1]
            sorted_spans = sorted(record_info, key=get_sort_key, reverse=True)
            result = []
            seen_tokens: Set[int] = set()
            for span in sorted_spans:
                # Check for end - 1 here because boundaries are inclusive
                if span[1] not in seen_tokens and span[2] - 1 not in seen_tokens:
                    result.append(span)
                    seen_tokens.update(range(span[1], span[2]))
            result = sorted(result, key=lambda span: span[1])

            return result

        # gather all potential info from the kb
        for rec in records:
            if copy_predictions and rec.prediction:
                ctx.query_params["word_dict_kb_predictions"] = update_word_dict_kb(
                    rec, rec.prediction, ctx.query_params["word_dict_kb_predictions"]
                )
            if copy_annotations and rec.annotation:
                ctx.query_params["word_dict_kb_annotations"] = update_word_dict_kb(
                    rec, rec.annotation, ctx.query_params["word_dict_kb_annotations"]
                )

        query_relevant = f'({" OR ".join(list(seen_words))})'


        # update the kb_info in the record
        new_records = rg.load(ctx.__listener__.dataset, query=query_relevant)
        updated_records = []
        for rec in new_records:
            rec_predictions_old = copy.deepcopy(rec.prediction)
            rec_annotations_old = copy.deepcopy(rec.annotation)
            if copy_predictions:
                validated_spans = apply_word_dict_kb(
                    rec, ctx.query_params["word_dict_kb_predictions"]
                )
                if rec.prediction is None:
                    rec.prediction = []
                rec.prediction += validated_spans
                rec.prediction = resolve_span_overlap(rec.prediction)
            if copy_annotations:
                validated_spans = apply_word_dict_kb(
                    rec, ctx.query_params["word_dict_kb_annotations"]
                )
                if rec.annotation is None:
                    rec.annotation = []
                rec.annotation = resolve_span_overlap(rec.annotation + [span[:-1] for span in validated_spans])
            if (
                rec_predictions_old != rec.prediction
                or rec_annotations_old != rec.annotation
            ):
                rec = rec.__class__(**rec.__dict__)
                updated_records.append(rec)

        if updated_records:
            log.info(f"updating {len(updated_records)} records")
            rg.log(
                records=updated_records,
                name=ctx.__listener__.dataset,
                verbose=False,
                chunk_size=20
            )

    log.info(f"copycat ready to mimick your annotations and predictions {query}.")

    return plugin
