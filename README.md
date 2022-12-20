# argilla-plugins
🔌 Open-source plugins for with practical features for Argilla using listeners.

**Why?**  The development time for actual features can be a bit high, however, to enable the community and allow for the production testing, we would like to allow for communicating reproducible plugins that might lateron be integrated in the actual product.


## Reporting

**What is it?** Automatically assign labels based on intuitive and emperical heuristic.

Plugins:
- [ ] automated reporting pluging using `datapane`. issue
- [ ] automated reporting pluging for `great-expectations`. issue

## Datasets

**What is it?** Everything that involves operations on a `dataset level`, like dividing work, syncing datasets, and deduplicating records.

Plugins:
- [ ] sync data between datasets
  - [ ] directional A->B. issue
  - [ ] bi-directional A <-> B. issue
- [ ] remove duplicate records. issue
- [ ] create train test splits. issue
- [ ] set limits to records in datasets
  - [ ] end of life time. issue
  - [ ] max # of records. issue

## Programmatic Labelling

**What is it?** Automatically update `annotations` and `predictions` labels and predictions of `records` on intuitive and emperical heuristic.

Plugins:
- [ ] annotated spans as gazzetteer for labelling. issue
- [ ] vector search queries and similarity threshold. issue
- [ ] use separate gezzetteer for labelling. issue

## Active learning

**What is it?** A process during which a learning algorithm can interactively query a user (or some other information source) to label new data points.

- [ ] active learning for `TextClassification`.
  - [ ] `classy-classification`. issue
  - [ ] `small-text`. issue
- [ ] active learning for `TokenClassification`. issue


## Suggestions
Do you have any suggestions? Please [open an issue](https://github.com/argilla-io/argilla-plugins/issues/new/choose) 🤓
