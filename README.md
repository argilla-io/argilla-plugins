# Argilla Plugins

> 🔌 Open-source plugins for extra features and workflows

**Why?**
The design of Argilla is intentionally programmable (i.e., developers can build complex workflows for reading and updating datasets). However, there are certain workflows and features which are shared across different use cases and could be simplified from a developer experience perspective. In order to facilitate the reuse of key workflows and empower the community, Argilla Plugins provides a collection of extensions to super power your Argilla use cases.
Some of this pluggable method could be eventually integrated into the [core of Argilla](https://github.com/argilla-io/argilla).

## How to develop a plugin

1. Pick a cool plugin from the list of topics or our issue overview.
2. Think about an abstraction for the plugin as shown below.
3. Refer to the solution in the issue.
   1. fork the repo.
   2. commit your code
   3. open a PR.
4. Keep it simple.
5. Have fun.

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
```python
from argilla_plugins.topic import plugin
plugin(name="dataset_name", ws="workspace" query="query", interval=1.0)
plugin.start()
```

#### Variables
variables `name`, `ws`, and `query` are supposed to be re-used as much as possible throughout all plugins. Similarly, some functions might contain adaptations like `name_from` or `query_from`. Whenever possible re-use variables as much as possible.

Ohh, and don`t forget to have fun! 🤓

## Topics
### Reporting

**What is it?**
Create interactive reports about dataset activity, dataset features, annotation tasks, model predictions, and more.

Plugins:
- [ ] automated reporting pluging using `datapane`. [issue](https://github.com/argilla-io/argilla-plugins/issues/1)
- [ ] automated reporting pluging for `great-expectations`. [issue](https://github.com/argilla-io/argilla-plugins/issues/2)

### Datasets

**What is it?**
Everything that involves operations on a `dataset level`, like dividing work, syncing datasets, and deduplicating records.

Plugins:
- [ ] sync data between datasets.
  - [ ] directional A->B. [issue](https://github.com/argilla-io/argilla-plugins/issues/3)
  - [ ] bi-directional A <-> B. [issue](https://github.com/argilla-io/argilla-plugins/issues/4)
- [ ] remove duplicate records. [issue](https://github.com/argilla-io/argilla-plugins/issues/5)
- [ ] create train test splits. [issue](https://github.com/argilla-io/argilla-plugins/issues/6)
- [ ] set limits to records in datasets
  - [X] end of life time. [issue](https://github.com/argilla-io/argilla-plugins/issues/7)
  - [ ] max # of records. [issue](https://github.com/argilla-io/argilla-plugins/issues/8)

#### End of Life
Automatically delete or discard records after `x` seconds.

```python
from argilla_plugins.datasets import end_of_life

plugin = end_of_life(
    name="plugin-test",
    end_of_life_in_seconds=100,
    execution_interval_in_seconds=5,
    discard_only=False
)
plugin.start()
```

### Programmatic Labelling

**What is it?**
Automatically update `annotations` and `predictions` labels and predictions of `records` based on heuristics.

Plugins:
- [ ] annotated spans as gazzetteer for labelling. [issue](https://github.com/argilla-io/argilla-plugins/issues/12)
- [ ] vector search queries and similarity threshold. [issue](https://github.com/argilla-io/argilla-plugins/issues/11)
- [ ] use gazzetteer for labelling. [issue](https://github.com/argilla-io/argilla-plugins/issues/9)
- [ ] materialize annotations/predictions from rules using Snorkel or a MajorityVoter [issue](https://github.com/argilla-io/argilla-plugins/issues/10)

### Active learning

**What is it?**
A process during which a learning algorithm can interactively query a user (or some other information source) to label new data points.

Plugins:
- [ ] active learning for `TextClassification`.
  - [ ] `classy-classification`. [issue](https://github.com/argilla-io/argilla-plugins/issues/13)
  - [ ] `small-text`. [issue](https://github.com/argilla-io/argilla-plugins/issues/15)
- [ ] active learning for `TokenClassification`. [issue](https://github.com/argilla-io/argilla-plugins/issues/17)

### Inference endpoints
**What is it?**
Automatically add predictions to records as they are logged into Argilla. This can be used for making it really easy to pre-annotated a dataset with an existing model or service.

- [ ] inference with un-authenticated endpoint. [issue](https://github.com/argilla-io/argilla-plugins/issues/16)
- [ ] embed incoming records in the background. [issue](https://github.com/argilla-io/argilla-plugins/issues/18)


### Training endpoints
**What is it?**
Automatically train a model based on dataset annotations.

- [ ] TBD

### Suggestions
Do you have any suggestions? Please [open an issue](https://github.com/argilla-io/argilla-plugins/issues/new/choose) 🤓
