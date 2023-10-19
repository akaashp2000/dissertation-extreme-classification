# coding=utf-8
# Copyright 2023 The Google Research Authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Various dataset and model training utilities."""
import os
from typing import List, Tuple

import dataclasses
import tensorflow as tf

import os
import requests

TFRECORD_URLS = {
    "train10": "http://storage.googleapis.com/gresearch/logit_adjustment/cifar10-lt_train.tfrecord",
    "test10": "http://storage.googleapis.com/gresearch/logit_adjustment/cifar10_test.tfrecord",
    "train100": "http://storage.googleapis.com/gresearch/logit_adjustment/cifar100-lt_train.tfrecord",
    "test100": "http://storage.googleapis.com/gresearch/logit_adjustment/cifar100_test.tfrecord",
}


def build_loss_fn(use_la_loss, base_probs, tau=1.0):
    """Builds the loss function to be used for training.

    Args:
      use_la_loss: Whether or not to use the logit-adjusted loss.
      base_probs: Base probabilities to use in the logit-adjusted loss.
      tau: Temperature scaling parameter for the base probabilities.

    Returns:
      A loss function with signature loss(labels, logits).
    """

    def loss_fn(labels, logits):
        if use_la_loss:
            logits = logits + tf.math.log(
                tf.cast(base_probs**tau + 1e-12, dtype=tf.float32)
            )
        loss = tf.nn.sparse_softmax_cross_entropy_with_logits(
            labels=labels, logits=logits
        )
        return tf.reduce_mean(loss, axis=0)

    return loss_fn


class LearningRateSchedule(tf.keras.optimizers.schedules.LearningRateSchedule):
    """Step learning rate schedule."""

    def __init__(self, schedule, steps_per_epoch, base_learning_rate):
        """Creates a step learning rate schedule.

        Args:
          schedule: List of (epoch_number, lr_multiplier) pairs. The base learning
            rate will be multiplied by the multiplier at the epoch number. The first
            entry says when to finish the linear warmup.
          steps_per_epoch: Number of steps per epoch.
          base_learning_rate: Base learning rate.
        """
        super().__init__()
        self._schedule = schedule
        self._steps_per_epoch = steps_per_epoch
        self._base_learning_rate = base_learning_rate

    def __call__(self, step):
        """See base class."""
        lr_epoch = tf.cast(step, tf.float32) / self._steps_per_epoch
        warmup_lr_multiplier, warmup_end_epoch = self._schedule[0]
        learning_rate = (
            self._base_learning_rate
            * warmup_lr_multiplier
            * lr_epoch
            / warmup_end_epoch
        )
        for mult, start_epoch in self._schedule:
            learning_rate = tf.where(
                lr_epoch >= start_epoch, self._base_learning_rate * mult, learning_rate
            )
        return learning_rate

    def get_config(self):
        """See base class."""
        return {
            "schedule": self._schedule,
            "steps_per_epoch": self._steps_per_epoch,
            "base_learning_rate": self._base_learning_rate,
        }


@dataclasses.dataclass
class Dataset:
    """Represents a dataset."""

    name: str
    num_classes: int
    train_file_name: str
    test_file_name: str
    num_train: int
    num_test: int
    num_epochs: int
    lr_schedule: List[Tuple[float, int]]


def dataset_mappings():
    """Returns dataset_name -> Dataset mappings."""
    return {
        "cifar10-lt": Dataset(
            "cifar10-lt",
            10,
            "cifar10-lt_train.tfrecord",
            "cifar10_test.tfrecord",
            12406,
            10000,
            200,
            [(1.0, 5), (0.1, 160), (0.01, 180)],  # (multiplier, epoch to start) tuples
        ),
        "cifar100-lt": Dataset(
            "cifar100-lt",
            100,
            "cifar100-lt_train.tfrecord",
            "cifar100_test.tfrecord",
            10847,
            10000,
            1419,
            [  # (multiplier, epoch to start) tuples
                (1.0, 22),
                (0.1, 691),
                (0.01, 1059),
                (0.001, 1290),
            ],
        ),
        "test": Dataset(
            "test", 10, "test.tfrecord", "test.tfrecord", 4, 4, 2, [(1.0, 2)]
        ),
    }


def _process_image(record, training):
    """Decodes the image and performs data augmentation if training."""
    image = tf.io.decode_raw(record, tf.uint8)
    image = tf.cast(image, tf.float32)
    image = tf.reshape(image, [32, 32, 3])
    image = image * (1.0 / 255) - 0.5
    if training:
        padding = 4
        image = tf.image.resize_with_crop_or_pad(image, 32 + padding, 32 + padding)
        image = tf.image.random_crop(image, [32, 32, 3])
        image = tf.image.random_flip_left_right(image)
    return image


def _parse(serialized_examples, training):
    """Parses the given protos and performs data augmentation if training."""
    feature_spec = {
        "image/encoded": tf.io.FixedLenFeature((), tf.string),
        "image/class/label": tf.io.FixedLenFeature((), tf.int64),
    }
    features = tf.io.parse_example(serialized_examples, feature_spec)
    images = tf.map_fn(
        lambda record: _process_image(record, training),
        features["image/encoded"],
        dtype=tf.float32,
    )
    return images, features["image/class/label"]


def create_tf_dataset(dataset, data_home, batch_size, training):
    """Creates a Tensorflow Dataset instance for training/testing.

    Args:
      dataset:    Dataset definition.
      data_home:  Directory where the .tfrecord files are stored.
      batch_size: Batch size.
      training:   Whether to return a training dataset or not. Training datasets
        have data augmentation.

    Returns:
      A tf.data.Dataset instance.
    """

    filename = dataset.train_file_name if training else dataset.test_file_name

    return (
        tf.data.TFRecordDataset(os.path.join(data_home, filename))
        .shuffle(10000)
        .batch(batch_size, drop_remainder=training)
        .map(lambda record: _parse(record, training))
        .prefetch(tf.data.experimental.AUTOTUNE)
    )


def download_tfrecord(*args, data_dir: str = "./data"):
    """
    Download TFRecord files from a predefined dictionary of URLs to a specified data directory.

    Args:
        *args: Variable number of strings representing the keys for TFRecord URLs.
        data_dir (str, optional): The directory where TFRecord files will be downloaded. Defaults to "./data".

    Description:
    This function allows you to download TFRecord files specified by their keys from a predefined dictionary of URLs. It checks if the files already exist in the data directory and prompts the user for confirmation before overwriting if necessary. The downloaded files are saved in the specified data directory.

    Parameters:
        *args (str): One or more keys corresponding to TFRecord URLs in the predefined dictionary.
        data_dir (str): The directory where the TFRecord files will be downloaded.

    Predefined Dictionary:
        The function uses a predefined dictionary, TFRECORD_URLS, which should be defined in the script. It maps keys to TFRecord URLs.

    Example:
        To download 'train-10' and 'test-10' TFRecord files to the 'data' directory:
        download_tfrecord("train10", "test10", data_dir="data")

    Note:
        Make sure to define the TFRECORD_URLS dictionary with the appropriate URL mappings in your script.
    """
    # Extract the file name from the URL
    args = [arg for arg in args if arg in TFRECORD_URLS.keys()]

    for arg in args:
        file_name = os.path.join(data_dir, TFRECORD_URLS[arg].split("/")[-1])

        write = "y"

        if os.path.exists(file_name):
            # The file already exists; ask for confirmation
            write = (
                input(
                    f"The file '{file_name}' already exists. Do you want to overwrite it? (y/n): "
                )
                .strip()
                .lower()
            )

        if write == "y":
            try:
                # Download the TFRecord file
                response = requests.get(TFRECORD_URLS[arg])
                response.raise_for_status()

                with open(file_name, "wb") as tfrecord_file:
                    tfrecord_file.write(response.content)
                print(f"Downloaded '{file_name}' to '{data_dir}'")

            except Exception as e:
                print(f"An error occurred while downloading the TFRecord file: {e}")
        else:
            print(f"Skipped '{file_name}'")
