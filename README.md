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

PRISM utilises the backbone of Stable Diffusion(SD) v1.5. 

```bash
torchrun --nproc_per_node=4 finetune_chexpert.py
```
> *Note: the command to finetune is `torchrun` and not `python`*

The `finetune_chexpert.py` script enables distributed training to fine-tune Stable Diffusion on chest X-ray images with associated pathology labels. The script:

1. Creates automatic captions based on pathology findings
2. Trains only the UNet component while freezing VAE and text encoder
3. Supports distributed training with mixed precision
4. Includes checkpoint saving and logging

Below are the important parameters that sets the paths:

| **Parameter** | **Default** | **Description** |
|--------|------|------------------|
| `--model_name_or_path` | `runwayml/stable-diffusion-v1-5` | Base pretrained model to fine-tune |
| `--train_data_path` | `/usr/local/.../finetune.csv` | Path to CheXpert CSV file with pathology labels |
| `--image_root_path` | `/usr/local/datasets/` | Root directory containing the chest X-ray images |
| `--output_dir` | `/usr/local/.../finetuned` | Directory to save the fine-tuned model and checkpoints |


> For fine-tuning, we use 4 A100 GPUs with 40GB each. The wall clock time to fine-tune SDv1.5 was 6 hours.


### Counterfactual Image Generation

```bash
python generate_cf_images.py
```
The `generate_cf_images.py` script uses a technique to generate counterfactual versions of chest X-ray images. 
#### Key Parameters

| **Parameter** | **Description** |
|--------|------------------|
| `ldm_type` | Type of diffusion model to use. Options: `stable_diffusion_v1_4`, `stable_diffusion_v1_5`, `stable_diffusion_mimic_cxr_v0.1`, `finetuned_chexpert` |
| `self_replace_steps_range` | Controls the strength of self-attention replacement during editing. Higher values result in stronger edits but less preservation of original structure |
| `edit_word_weight` | Emphasis placed on the edit word in the prompt. Higher values lead to stronger edits |
| `clip_img_thresh` | Threshold for image-image similarity (higher = more similar to original) |
| `clip_thresh` | Threshold for image-text similarity |
| `clip_dir_thresh` | Threshold for directional similarity (measures if edit is in the right direction) |
| `text_similarity_threshold` | Controls filtering of edits based on text similarity to ground truth |

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
