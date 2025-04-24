# PRISM: High-Resolution and Precise Counterfactual Medical Image Generation using Language-guided Stable Diffusion
This is the official repository of the PRISM (submitted to Medical Imaging with Deep Learning (MIDL 2025)).

PRISM - **Pr**ecise counterfactual **I**mage generation using language guided **S**table diffusion **M**odel

<div align="center">
  
[![arXiv](https://img.shields.io/badge/arXiv-2503.00196-b31b1b.svg)](https://arxiv.org/abs/2503.00196)
[![Website](https://img.shields.io/badge/Website-PRISM-9370DB.svg)](https://amarkr1.github.io/PRISM/)
[![OpenReview](https://img.shields.io/badge/OpenReview-Reviews-blue.svg)](https://openreview.net/forum?id=UpJMAlZNuo)
[![Hugging Face](https://img.shields.io/badge/🤗_Hugging_Face-PRISM-yellow.svg)](https://huggingface.co/amar-kr/PRISM)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
</div>

<p align="center">
<picture>
  <img src="https://github.com/Amarkr1/PRISM/blob/website/images/arch_v2.png">
</picture>
</p>



## Table of Contents
- [Repository Structure](#repository-structure)
- [Getting Started](#getting-started)
  - [Virtual Environment Setup](#virtual-environment-setup)
  - [Create Dataset](#create-dataset)
- [Core Functionalities](#core-functionalities)
  - [Finetuning Stable Diffusion](#finetune-stable-diffusion)
  - [Counterfactual Image Generation](#counterfactual-image-generation)
  - [Classifiers](#classifiers)
- [Baselines](#baselines)
  - [Cycle-GAN](#cycle-gan)
  - [Others](#others)   
- [Examples](#examples)
- [Citation](#citation)


## Repository Structure

This repository is organized into two branches:
- **`main`**: Contains all source code and implementation files
- **`website`**: Houses the project website and documentation assets

> #### You are currently on the <u>*main*</u> branch of this repository. Visit the [website](https://github.com/Amarkr1/PRISM/tree/website) branch to access the website files and source code.


## Getting Started
### Virtual Environment Setup
Create a virtual Environment and install the necessary packages from the `requirements.txt` file as shown:
```bash
pip install -r requirements.txt --no-cache
```
> Note: The `transformers` and `diffusers` libraries version must match as specified in the `requirements.txt`. In case of error due to library mismatch, `huggingface_hub==0.25.2` can also be installed.


### Create Dataset

**Data Preparation**: Signup to access the CheXpert dataset from [here](https://stanfordmlgroup.github.io/competitions/chexpert/). Split the dataset into 70-15-15 for the train-validation-test split. This split will remain the same for all the experiments.

## Core Functionalities
### Finetune Stable Diffusion

PRISM utilises the backbone of Stable Diffusion v1.5. 

### Counterfactual Image Generation

### Classifiers

## Baselines
### Cyle-GAN

### Other

## Examples
<table border="0" cellspacing="0" cellpadding="0" style="border:none; border-collapse:collapse;">
  <tr>
    <td width="50%" style="border:none;"><img src="https://github.com/Amarkr1/PRISM/blob/website/images/animation5.gif" alt="Medical Device Editing" width="100%"></td>
    <td width="50%" style="border:none;"><img src="https://github.com/Amarkr1/PRISM/blob/website/images/animation4.gif" alt="XAI" width="100%"></td>
  </tr>
  <tr>
    <td align="center" style="border:none;"><strong>Editing Medical Devices using PRISM</strong></td>
    <td align="center" style="border:none;"><strong>XAI using PRISM</strong></td>
  </tr>
</table>

## Citation
```bibtex
@misc{kumar2025prism,
title={PRISM: High-Resolution \& Precise Counterfactual Medical Image Generation using Language-guided Stable Diffusion},
author={Kumar, Amar and Kriz, Anita and Havaei, Mohammad and Arbel, Tal},
eprint={2503.00196},
url={https://arxiv.org/abs/2503.00196},
year={2025}
}
```
## Acknowledgements
PRISM is built on top of several excellent repositories - [LANCE](https://github.com/virajprabhu/LANCE), [Prompt-to-prompt](https://github.com/google/prompt-to-prompt/). For comparisons, we also use codes from the repositories - [RadEdit](https://huggingface.co/microsoft/radedit), [Imagic](https://github.com/sangminkim-99/Imagic/), [Null-Text Inversion](https://null-text-inversion.github.io/). Additionally, we leverage and borrow a few techniques from [Instruct-Pix2Pix](https://github.com/timothybrooks/instruct-pix2pix), [huggingface-transformers](https://github.com/huggingface/transformers).
