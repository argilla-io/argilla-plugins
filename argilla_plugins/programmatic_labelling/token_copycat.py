import copy
import logging
import re
import string
from typing import Any, Dict, List, Set, Tuple

import argilla as rg
from argilla import listener


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

    if word_dict_kb_annotations is None:
        word_dict_kb_annotations = {}
    if word_dict_kb_predictions is None:
        word_dict_kb_predictions = {}

    log = logging.getLogger(f"token_classification_copycat | {name}")

    @listener(
        dataset=name,
        query=query,
        *args,
        **kwargs,
        word_dict_kb_predictions=word_dict_kb_predictions,
        word_dict_kb_annotations=word_dict_kb_annotations,
    )
    def plugin(records, ctx):
        def get_spans_from_tokens(tokens: List[str]):
            """
            get [(start, end)] for each token w.r.t. the entire list of tokens
            """
            spans = []
            start = 0
            for token in tokens:
                end = start + len(token)
                spans.append((start, end))
                start = end
            return spans

        def get_all_combinations_of_adjacent_spans(spans: List[tuple]) -> List[tuple]:
            """
            Takes a list of adjacent spans and returns a list of all the combinations of adjacent spans.
            """
            combinations = []
            for i in range(len(spans)):
                for j in range(i + 1, len(spans) + 1):
                    # TODO: this is a hack to avoid combinations that are too long
                    if spans[j - 1][1] - spans[i][0] > 50:
                        break
                    combinations.append(spans[i:j])
            start_end_combinations = []
            for combination in combinations:
                start_end_combinations.append((combination[0][0], combination[-1][1]))
            return start_end_combinations

        def check_alignment_span_with_list_of_spans(
            spans: List[tuple], allowed_spans: List[tuple]
        ) -> bool:
            """
            Check if a span is aligned with a range of one or more of a list of adjacent spans.
            """
            accepted_spans = []
            for span in spans:
                if span in allowed_spans:
                    accepted_spans.append(True)
                else:
                    accepted_spans.append(False)

            return accepted_spans

        def validate_token_boundary(record_info, tokens):
            spans = get_spans_from_tokens(tokens)
            allowed_spans = get_all_combinations_of_adjacent_spans(spans)
            optional_spans = [(rec[1], rec[2]) for rec in record_info]
            span_mask = check_alignment_span_with_list_of_spans(
                optional_spans, allowed_spans
            )
            accepted_spans = [
                span for span, mask in zip(record_info, span_mask) if mask
            ]
            return accepted_spans

        def apply_word_dict_kb(
            rec: Any, word_dict: Dict[str, Dict[str, Any]]
        ) -> List[Tuple[str, int, int, float]]:
            """
            For each know label and known word, get the character span from the text and assign it to the predictions as
            [(label, start, end, 0)]
            """
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
                            record_info.append(
                                (word_info["label"], s, end, word_info["score"])
                            )
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
            get_sort_key = lambda record_info: (
                record_info[2] - record_info[1],
                -record_info[1],
            )
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

        # update the kb_info in the record
        updated_records = []
        for rec in records:
            rec_predictions_old = copy.deepcopy(rec.prediction)
            rec_annotations_old = copy.deepcopy(rec.annotation)
            if copy_predictions:
                record_info = apply_word_dict_kb(
                    rec, ctx.query_params["word_dict_kb_predictions"]
                )
                validated_spans = validate_token_boundary(record_info, rec.tokens)
                rec.prediction += validated_spans
                rec.prediction = resolve_span_overlap(rec.prediction)
            if copy_annotations:
                record_info = apply_word_dict_kb(
                    rec, ctx.query_params["word_dict_kb_annotations"]
                )
                validated_spans = validate_token_boundary(record_info, rec.tokens)
                rec.annotation += validated_spans
                rec.annotation = resolve_span_overlap(rec.annotation)
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
            )

    log.info(f"copycat ready to mimick your annotations and predictions {query}.")

    return plugin
