# argilla-plugins
🔌 Open-source plugins for with practical features for Argilla using listeners.

**Why?**  The development time for actual features can be a bit high, however, to enable the community and allow for the production testing, we would like to allow for communicating reproducible plugins that might lateron be integrated in the actual product.

## How to develop a plugin

1. Pick a cool plugin from the list of topics or our issue overview.
2. Refer to the solution in the issue
   1. fork the repo
   2. open a PR
3. Think about an abstraction for the plugin as shown below
4. Keep it simple -
5. Have fun.


### Development requirements

#### Function
We want to to keep the plugins as abstract as possible, hence they have to be able to be used within 3 lines of code.
```
from argilla_plugins.topic import pluging
plugin(name="dataset_name", ws="workspace" query="query", interval=1.0)
plugin.start()
```

#### Variables
variables `name`, `ws`, and `query` are supposed to be re-used as much as possible throughout all plugins. Similarly, some functions might contain adaptations like `name_from` or `query_from`. Whenever possible re-use variables as much as possible.

Ohh, and don`t forget to have fun! 🤓

## Topics
### Reporting

**What is it?** Reporting and monitoring data is important and help to get some info. Can we get some basic info for reports.

Plugins:
- [ ] automated reporting pluging using `datapane`. issue
- [ ] automated reporting pluging for `great-expectations`. issue

### Datasets

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

### Programmatic Labelling

**What is it?** Automatically update `annotations` and `predictions` labels and predictions of `records` on intuitive and emperical heuristic.

Plugins:
- [ ] annotated spans as gazzetteer for labelling. issue
- [ ] vector search queries and similarity threshold. issue
- [ ] use separate gezzetteer for labelling. issue

### Active learning

**What is it?** A process during which a learning algorithm can interactively query a user (or some other information source) to label new data points.

Plugins:
- [ ] active learning for `TextClassification`.
  - [ ] `classy-classification`. issue
  - [ ] `small-text`. issue
- [ ] active learning for `TokenClassification`. issue


### Suggestions
Do you have any suggestions? Please [open an issue](https://github.com/argilla-io/argilla-plugins/issues/new/choose) 🤓
