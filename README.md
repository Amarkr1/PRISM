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

## Editing Medical Devices usign PRISM

![remove_dev](https://github.com/Amarkr1/PRISM/blob/website/images/animation5.gif)

## XAI using PRISM
![XAI](https://github.com/Amarkr1/PRISM/blob/website/images/animation4.gif)

## Table of Contents
- [Create Virtual Environment](#create-virtual-environment-venv)
- [Create Datasets](#create-datasets)
- [Finetune Stable Diffusion](#finetune-stable-diffusion)
- [Counterfactual Image Generation](#counterfactual-image-generation)
- [Classifiers](#classifiers)
- [Citation](#citation)

## Create Virtual Environment Venv
Create a virtual Environment and install the nessecary packages from the `requirements.txt` file as shown:
```bash
pip install -r requirements.txt --no-cache
```

## Create Datasets

**Data Preparation**: Signup to access the CheXpert dataset from [here](https://stanfordmlgroup.github.io/competitions/chexpert/). Split the dataset into 70-15-15 for the train-validation-test split. This split will remain the same for all the experiments


## Finetune Stable Diffusion

PRISM utilises the backbone of Stable Diffusion v1.5. 

## Counterfactual Image Generation

## Classifiers

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
