import dataclasses
import os
import time
from threading import Thread
from typing import Optional, Set

from datasets import Dataset, load_dataset

import argilla as rg
from argilla.client.sdk.commons.errors import NotFoundApiError
from argilla.server.commons.models import TaskType


@dataclasses.dataclass
class Config:

    hf_source: Optional[str] = None
    hf_target: Optional[str] = None
    hf_token: Optional[str] = None
    hf_split: str = "train"
    hf_push_to_hub_frequency: int = 60

    rg_task: TaskType = TaskType.text_classification
    rg_dataset: Optional[str] = None
    rg_query: Optional[str] = None
    rg_labels: Optional[Set[str]] = None
    rg_multi_label_dataset: Optional[bool] = None
    rg_log_batch_size: int = 200
    rg_load_batch_size: int = 200

    def __post_init__(self):

        if not (self.hf_source or self.hf_target or self.rg_dataset):
            raise ValueError("Must specify a source/target dataset or an rg_dataset")

        if not self.rg_dataset:
            dataset_name = self.hf_target or self.hf_source
            self.rg_dataset = dataset_name.split("/")[-1]

        if not self.hf_target:
            self.hf_target = self.hf_source or self.rg_dataset  # must provide an org????

        self.hf_token = self.hf_token or os.environ.get("HF_TOKEN")


class HuggingfaceSync(Thread):
    def __init__(self, config: Config, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._config = config
        self.stop = False

    def run(self) -> None:

        self.import_data()

        while not self.stop:
            time.sleep(self._config.hf_push_to_hub_frequency)
            self.export_data()

    def import_data(self):
        """Import data from HF hub to Argilla"""

        if not self._exist_argilla_dataset():
            hf_dataset = self._load_dataset_safety(self._config.hf_source, split=self._config.hf_split)

            if not hf_dataset:
                return

            self._log_hf_dataset(hf_dataset)

        if self._config.hf_source != self._config.hf_target or self._exist_argilla_dataset():

            target_ds = self._load_dataset_safety(self._config.hf_target, split=self._config.hf_split)

            if not target_ds:
                return

            self._log_hf_dataset(target_ds)

    def export_data(self):
        """Export data from Argilla to HF hub"""
        if not self._config.hf_token:
            return

        rg_dataset = rg.load(
            self._config.rg_dataset,
            query=self._config.rg_query,
            batch_size=self._config.rg_load_batch_size,
        )

        if not rg_dataset:
            return

        hf_dataset = rg_dataset.to_datasets()
        hf_dataset.push_to_hub(self._config.hf_target, token=self._config.hf_token, split=self._config.hf_split)

    def _log_hf_dataset(self, dataset: Dataset):

        task = self._config.rg_task
        if task == TaskType.text_classification:
            ds_class = rg.DatasetForTextClassification
        elif task == TaskType.token_classification:
            ds_class = rg.DatasetForTokenClassification
        elif task == TaskType.text2text:
            ds_class = rg.DatasetForText2Text
        else:
            raise RuntimeError(f"Wrong task {task}")

        records = ds_class.from_datasets(dataset)

        if ds_class == rg.DatasetForTextClassification and self._config.rg_multi_label_dataset:
            for record in records:
                record.multi_label = True

        self._prepare_dataset()
        rg.log(records, name=self._config.rg_dataset, batch_size=self._config.rg_log_batch_size)

    def _exist_argilla_dataset(self):

        try:
            rg.load(name=self._config.rg_dataset, limit=1)
            return True
        except NotFoundApiError:
            return False

    def _load_dataset_safety(self, dataset: str, split: str) -> Optional[Dataset]:
        try:
            return load_dataset(dataset, split=split, use_auth_token=self._config.hf_token)
        except:
            return None

    def _prepare_dataset(self):
        task = self._config.rg_task
        labels = self._config.rg_labels

        if not task in [TaskType.text_classification, TaskType.token_classification]:
            return

        if not labels:
            return

        if task == TaskType.text_classification:
            settings_cls = rg.TextClassificationSettings
        else:
            settings_cls = rg.TokenClassificationSettings

        rg.configure_dataset(name=self._config.rg_dataset, settings=settings_cls(label_schema=labels))


def hf_sync(
    hf_source: Optional[str] = None,
    hf_target: Optional[str] = None,
    hf_token: Optional[str] = None,
    hf_split: str = "train",
    hf_push_to_hub_frequency: int = 60,

    rg_task: TaskType = TaskType.text_classification,
    rg_dataset: Optional[str] = None,
    rg_query: Optional[str] = None,
    rg_labels: Optional[Set[str]] = None,
    rg_multi_label_dataset: Optional[bool] = None,
    rg_log_batch_size: int = 200,
    rg_load_batch_size: int = 200,
):
    """Syncs an Argilla dataset with a dataset in HF"""

    config = Config(
        hf_source=hf_source,
        hf_target=hf_target,
        hf_token=hf_token,
        hf_split=hf_split,
        hf_push_to_hub_frequency=hf_push_to_hub_frequency,

        rg_task=rg_task,
        rg_dataset=rg_dataset,
        rg_query=rg_query,
        rg_labels=rg_labels,
        rg_multi_label_dataset=rg_multi_label_dataset,
        rg_log_batch_size=rg_log_batch_size,
        rg_load_batch_size=rg_load_batch_size,
    )

    plugin = HuggingfaceSync(config)

    return plugin
