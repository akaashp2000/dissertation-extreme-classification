# Extreme Classification

This repository contains the code used and run to obtain experimental results for my dissertation.

Specifically it contains:
* notebooks for experiments on 2D synthetic data
    * one for Figures 2, 3 and 4 - binary problem
    * one for Figures 5 and 6 - multiclass problem
* modified code for CIFAR-10 experiments
    * a clone of the code for ["Long-tail learning via logit adjustment" (Menon et. al)](https://arxiv.org/abs/2007.07314)
        * a notebook for Table 1 and Figure 1
    * a clone of the code for ["Learning Imbalanced Datasets with Label-Distribution-Aware Margin Loss" (Cao et. al)](https://arxiv.org/abs/1906.07413)
        * a notebook for Table 2 and Figures 7, 8 and 9
        * Note: this is not currently working for CPU. It only works for GPU.
* a pdf copy of the dissertation
* ```requirements.txt``` file to set up virtualenv

## Set up

1. Clone the repo.

```bash
git clone https://github.com/akaashp2000/dissertation-extreme-classification
```

2. Within the ```dissertation-extreme-classification``` directory, create a virtual environment and install the requirements.

```bash
cd dissertation-extreme-classification
virtualenv venv
pip install -r requirements.txt
```

## Dissertation

The pdf file is available in the `dissertation` folder, called `thesismain.pdf`. 

The LaTeX source files can be found in the submodule `dissertation-extreme-classification-latex`, whose repo is [here](https://github.com/akaashp2000/dissertation-extreme-classification). The source files are currently private, so will require permission to view.

## Synthetic data experiments

These are in the `extreme-classification` directory.

There are two notebooks: one for the binary problem, and one for the multiclass problem, in the `notebooks` subdirectory. They plots they generate are saved to the `data` subdirectory. 

They both follow the same structure:
1. imports and set-up
2. define helper functions and models
3. generate the dataset
4. train models
5. generate and save plots

## Modified code

See the `LDAM-DRW` and `logit_adjustment` directories for the modified code for these projects. They include READMEs, which I have modified to reflect my changes, and the notebooks for my dissertation.

## Final note

Thank you for looking at my work! If you have any questions, please let me know by email: akaashp2000@gmail.com.