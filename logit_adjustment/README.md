# Long-tail learning via logit adjustment

Aditya Krishna Menon, Sadeep Jayasumana, Ankit Singh Rawat, Himanshu Jain, Andreas Veit, Sanjiv Kumar.
ICLR 2021.
_________________

This code accompanies the paper [Long-tail learning via logit adjustment](https://arxiv.org/abs/2007.07314).

Here we have modified the [original code](https://github.com/google-research/google-research/tree/master/logit_adjustment) and added a notebook to get the results (Table 1 and Figure 1) in the dissertation.

## Running the code

### Dataset

The original data (imbalanced CIFAR datasets) can be downloaded via the links:
* [cifar10-lt_train.tfrecord](http://storage.googleapis.com/gresearch/logit_adjustment/cifar10-lt_train.tfrecord)
* [cifar10_test.tfrecord](http://storage.googleapis.com/gresearch/logit_adjustment/cifar10_test.tfrecord)
* [cifar100-lt_train.tfrecord](http://storage.googleapis.com/gresearch/logit_adjustment/cifar100-lt_train.tfrecord)
* [cifar100_test.tfrecord](http://storage.googleapis.com/gresearch/logit_adjustment/cifar100_test.tfrecord)

or with the ```download_tfrecord``` function in ```utils.py``` (which can be run through the notebook).

For the dissertation we need the CIFAR-10 datasets.

### Training (and evaluation)

We need the `.tfrecord` files in the `data` directory for training and evaluation. The train datasets were created with the EXP-100 profile as detailed in the paper, the
test datasets are the same as the standard CIFAR-10/100 test datasets.

See the notebook ```logit_adjustment.ipynb``` for commands to train on the imbalanced CIFAR-10 with different losses.

Below is an example:

To train the ERM baseline on long-tailed imbalance with ratio of 100

```python main.py --dataset=cifar10-lt --mode=baseline```

This will train the models and evaluate them on the imbalanced train and balanced test sets. 

It will log metrics like train and test and accuracy to the log directory with Tensorboard. You can view the results directly via Tensorboard, or see below.

## Results

See the "Read the results" section in the notebook.

Here we reproduce Table 1 and Figure 1.

Table 1: the final epoch accuracies on the test set. We display these in a pandas DataFrame.

Figure 1: Altair bar charts to show the effective class probabilities with different values of $\beta$.