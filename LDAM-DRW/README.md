## Learning Imbalanced Datasets with Label-Distribution-Aware Margin Loss 
Kaidi Cao, Colin Wei, Adrien Gaidon, Nikos Arechiga, Tengyu Ma
_________________

This is the official implementation of LDAM-DRW in the paper [Learning Imbalanced Datasets with Label-Distribution-Aware Margin Loss](https://arxiv.org/pdf/1906.07413.pdf) in PyTorch.

### Dependencies

See the main README.md (in the parent directory).

### Dataset

- Imbalanced [CIFAR](https://www.cs.toronto.edu/~kriz/cifar.html). The original data will be downloaded and converted by `imbalance_cifar.py` - though you do not need to run this directly (see below)

### Training 

See the notebook ```ldam_drw.ipynb``` for commands to train on the imbalanced CIFAR 10 with different losses: specifically the sections (in Training (and evaluation) > Experiments and Results) Cao et. al, Cui et. al and Additional Experiments to run the training and evaluation.

Below is an example:

- To train the ERM baseline on long-tailed imbalance with ratio of 100

```bash
python cifar_train.py --gpu 0 --imb_type exp --imb_factor 0.01 --loss_type CE --train_rule None
```

This will use the CIFAR 10 dataset in the ```data``` directory. If that directory does not exist, or the dataset has not been downloaded, these commands will create the directory and download it there.

This will train the models and evaluate them on the imbalanced train and balanced test sets. It will log metrics like train or test loss and accuracy (overall and per-class) to the ```log``` directory with Tensorboard. You can view the results directly via Tensorboard, or see below.

### Results

See the Read the results section in the notebook.

Here we reproduce Table 2 and Figures 7, 8 and 9.

Table 2: the final epoch and best (across epochs) accuracies on the test set. We display a pandas DataFrame with these in.

Figures 7 and 8: Altair bar charts of per-class test accuracies (they are interactive so select relevant losses to match the Figures by SHIFT+click on the legend).

Figure 9: Altair line chart of train accuracy over time (epoch). It is interactive so select relevant losses to match the Figure by SHIFT click on the legend.