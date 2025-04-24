import os
import warnings
import time
import json
import functools
import argparse
from typing import Dict, Optional
import torch
from accelerate import Accelerator
from accelerate.logging import get_logger

torch.backends.cuda.matmul.allow_tf32 = True
from torchvision import transforms
from diffusers import StableDiffusionPipeline, DDIMScheduler
from transformers import AutoModel, AutoTokenizer, BertTokenizer
from safetensors.torch import load_file
from utils.misc_utils import *
from utils.edit_utils import *
import logging

# Configure logger to save logs to a file
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
timestamp = time.strftime("%Y%m%d-%H%M")
file_handler = logging.FileHandler(f'out/image_editor_{timestamp}.log')
file_handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

class ImageEditor:
    def __init__(
        self,
        args: argparse.Namespace,
        device: torch.device,
        self_replace_steps_range: Optional[list] = [0.4, 0.5, 0.6, 0.7, 0.8],
        cross_replace_steps: Optional[dict] = {"default_": 0.8},
        similarity_metric: Optional[ClipSimilarity] = ClipSimilarity(),
        text_similarity_threshold: Optional[float] = 0.5,
        ldm_type: Optional[str] = "stable_diffusion_v1_4",
        verbose: Optional[bool] = False,
        save_inversion: Optional[bool] = True,
        edit_word_weight: Optional[float] = 2.0,
        clip_img_thresh: Optional[float] = 0.6,
        clip_thresh: Optional[float] = 0.1,
        clip_dir_thresh: Optional[float] = -0.5,
    ):
        """
        Initialize image editor
        Args:
            args: Command line arguments from argparse
            device: Device to run model on
            self_replace_steps_range: Range of self replace steps to use. Defaults to [0.4, 0.5, 0.6, 0.7, 0.8].
            cross_replace_steps: Dictionary mapping image names to cross replace steps. Defaults to {"default_": 0.8}.
            similarity_metric: Similarity metric to use. Defaults to ClipSimilarity().
            text_similarity_threshold: Similarity threshold between . Defaults to 0.7
            ldm_type: Type of latent diffusion model to use. Defaults to "stable_diffusion_v1_4".
            verbose: Logging verbosity. Defaults to False.
            save_inversion: Whether to save image inversion. Defaults to True.
            edit_word_weight: Edit word weight. Defaults to 2.0.
            clip_img_thresh: Image similarity threshold. Defaults to 0.7.
            clip_thresh: Text similarity threshold. Defaults to 0.2.
            clip_dir_thresh: Directional similarity threshold. Defaults to 0.2.
        """
        self.args = args
        self.device = device
        self.self_replace_steps_range = self_replace_steps_range
        self.cross_replace_steps = cross_replace_steps
        self.clip_similarity = similarity_metric
        self.text_similarity_threshold = text_similarity_threshold
        self.ldm_type = ldm_type
        self.verbose = verbose
        self.save_inversion = save_inversion
        self.edit_word_weight = edit_word_weight
        self.clip_img_thresh = clip_img_thresh
        self.clip_thresh = clip_thresh
        self.clip_dir_thresh = clip_dir_thresh
        if self.verbose:
            logger.info(f"[Loading {ldm_type}]")

        # Using default hyperparams from Prompt-to-prompt
        scheduler = DDIMScheduler(
            beta_start=0.00085,
            beta_end=0.012,
            beta_schedule="scaled_linear",
            clip_sample=False,
            set_alpha_to_one=False,
            steps_offset=1,
        )
        t0 = time.time()
        with warnings.catch_warnings():
            warnings.simplefilter(action="ignore", category=FutureWarning)
            if ldm_type == "stable_diffusion_v1_5":
                self.model = StableDiffusionPipeline.from_pretrained(
                    "runwayml/stable-diffusion-v1-5",
                    scheduler=scheduler,
                )
            elif ldm_type == "stable_diffusion_v1_4":
                self.model = StableDiffusionPipeline.from_pretrained(
                    "CompVis/stable-diffusion-v1-4",
                    scheduler=scheduler,
                )
            elif ldm_type == "stable_diffusion_mimic_cxr_v0.1":
                print(f"[Loading {ldm_type}]")
                self.model = StableDiffusionPipeline.from_pretrained(
                    "IrohXu/stable-diffusion-mimic-cxr-v0.1",
                    scheduler=scheduler,
                )
            elif ldm_type == "finetuned_chexpert":
                print(f"[Loading {ldm_type}]")
                
                self.model = StableDiffusionPipeline.from_pretrained(
                    "runwayml/stable-diffusion-v1-5", scheduler=scheduler,
                )
                checkpoint = load_file("./saved_models/finetuned/checkpoints/model.safetensors")
                self.model.unet.load_state_dict(checkpoint)
            
            else:
                logger.error("Not implemented, exiting")
                raise NotImplementedError
        if self.verbose:
            logger.debug(f"Time to load model: {time.time() - t0:.02f} seconds.")

        self.model.to(device)
        self.inverter = NullInversion(self.model, device)

    def invert(self, img_path: str, prompt: str, img_inv_dir: str):
        """
        Invert image
        Args:
            img_path: Path to image to invert
            img_inv_dir: Path to which to save image inversion
        Returns:
            img_inv (Image): Inverted image
            prompt (str): Prompt used to invert image
            x_t (torch.Tensor): Latent vector used to invert image
            uncond_embeddings (torch.Tensor): Unconditional embeddings used to invert image
        """
        img_name = img_path.split("/")[-1].split(".")[0]
        if self.verbose:
            logger.info(">> Inverting image\n")

        if os.path.exists(os.path.join(img_inv_dir, img_name, "img_inv.jpeg")):
            if self.verbose:
                logger.warning(
                    f"=> Image `{img_name}' already inverted, loading from disk"
                )
            img, img_inv, x_t, uncond_embeddings = self.inverter.load_inversion(
                img_path, img_inv_dir
            )
            # Transfer x_t and uncond_embeddings to device
            x_t = x_t.to(self.device)
            uncond_embeddings = [emb.to(self.device) for emb in uncond_embeddings]

        else:
            if self.verbose:
                logger.info(f"=> Performing null-text inversion on {img_name}")
            (image_gt, _), x_t, uncond_embeddings = self.inverter.invert(
                img_path, prompt, offsets=(0, 0, 0, 0), num_inner_steps=10
            )
            controller = AttentionStore()
            image_inv, x_t = run_and_display(
                self.model,
                [prompt],
                controller,
                latent=x_t,
                uncond_embeddings=uncond_embeddings,
            )

            img = Image.fromarray(image_gt)
            img_inv = Image.fromarray(image_inv[0])

            if self.save_inversion:
                self.inverter.save_inversion(
                    img_path, img, img_inv, x_t, uncond_embeddings, img_inv_dir
                )
                if self.verbose:
                    logger.info(f"=> Saved inversion")
        return img, img_inv, x_t, uncond_embeddings

    def edit(
        self,
        out_path: str,
        cls_name: str,
        x_t: torch.Tensor,
        uncond_embeddings: torch.Tensor,
        cap: str,
        edited_cap_dicts: List[Dict[str, str]],
    ):
        """
        Edit image
        Args:
            out_path: Path to save edited image
            cls_name: Class name
            x_t: Latent vector inversion of image
            uncond_embeddings: Unconditional embeddings of image
            cap: Caption of image
            edited_caps: Edited captions of image
        """
        if self.verbose:
            logger.info("Editing image\n")
            logger.info("------------------------------------------------\n")

        prompt_dict = {
            "caption": cap,
            "image": out_path.split("/")[-1],
            "edits": {},
        }
        # Filter out edits that are more similar to the ground truth class than a threshold
        edited_cap_dicts_filtered = [
            edited_cap
            for edited_cap in edited_cap_dicts
            if (
                self.clip_similarity.text_similarity(
                    [edited_cap["original"].strip().lower()], [cls_name]
                )
                < self.text_similarity_threshold
            )
            or (edited_cap["original"].strip().lower() == "")
        ]
        

        if len(edited_cap_dicts_filtered) == 0:
            if self.verbose:
                logger.warning(
                    "All target words are too similar to ground truth class. \
                    Skipping this image. Increase text_similarity_threshold if you \
                    want to force an edit."
                )
            return

        total_memory = (torch.cuda.mem_get_info()[0]) // 10**9
        edit_batch_size = max(total_memory // 8, 1)
        
        for ix in range(0, len(edited_cap_dicts_filtered), edit_batch_size):
            edited_cap_dicts_filtered_curr = edited_cap_dicts_filtered[
                ix : min(ix + edit_batch_size, len(edited_cap_dicts_filtered))
            ]
                        
            edited_caps = [
                edited_cap["edited_caption"]
                for edited_cap in edited_cap_dicts_filtered_curr
            ]
            originals = [
                edited_cap["original"] for edited_cap in edited_cap_dicts_filtered_curr
            ]
            edits = [
                edited_cap["edit"] for edited_cap in edited_cap_dicts_filtered_curr
            ]
            
            edit_concat = "".join(
                ["{}->{}\n".format(a, b) for a, b in zip(originals, edits)]
            )
            if self.verbose:
                logger.info(f"Original prompt: {cap}")
                logger.info(edit_concat)

            cur_prompts = [cap]
            cur_prompts.extend(edited_caps)

            eq_params = {
                "words": (edit for edit in edits),
                "values": (self.edit_word_weight for _ in range(len(edits))),
            }
            blend_words = (
                ((original,), (edit,)) for original, edit in zip(originals, edits)
            )
            if self.verbose:
                logger.info(f"Running sweep over editing hyperparams:\n")

                        
            
            attention_replace_edit = False
            for self_replace_steps in self.self_replace_steps_range:
                controller = make_controller(
                    cur_prompts,
                    self.device,
                    self.model.tokenizer,
                    attention_replace_edit,
                    self.cross_replace_steps,
                    float(self_replace_steps),
                    blend_words,
                    eq_params,
                )
                if self.verbose:
                    logger.info(f"self_replace_steps={self_replace_steps}")

                images, _ = run_and_display(
                    self.model,
                    cur_prompts,
                    controller,
                    latent=x_t,
                    uncond_embeddings=uncond_embeddings,
                    verbose=False,
                )
                tns1 = transforms.ToTensor()(images[0]).unsqueeze(0).to(self.device)
                tns2 = torch.cat(
                    [
                        transforms.ToTensor()(images[ix]).unsqueeze(0)
                        for ix in range(1, len(images))
                    ],
                    dim=0,
                ).to(self.device)
                if self.verbose:
                    logger.info(f"Evaluating edit quality and consistency\t")
                    logger.info("-------------\n")
                    logger.info(f"Original caption: {cap}\n")
                    logger.info(f"Edited captions: {edited_caps}\n")
                (
                    clip_sim_0,
                    clip_sim_1,
                    clip_sim_dir,
                    clip_sim_image,
                ) = self.clip_similarity(tns1, tns2, [cap], edited_caps)

                best_sim_dir = [-1 for _ in range(len(clip_sim_dir))]
                
                for ix in range(len(clip_sim_dir)):
                    prediction_is_consistent = (
                        self.clip_similarity.pred_consistency(  # predictive consistency
                            tns2[ix : ix + 1], originals[ix], edits[ix]
                        )
                    )
                    if self.verbose:
                        logger.info(
                            "[Metrics] I1I2={:.2f} I1T1={:.2f} I2T2={:.2f} <I1I2, T1T2>={:.2f} PC={}".format(
                                clip_sim_image[ix].item(),
                                clip_sim_0.item(),
                                clip_sim_1[ix].item(),
                                clip_sim_dir[ix].item(),
                                prediction_is_consistent,
                            )
                        )
                    #print("clip_sim_image", clip_sim_image[ix])
                    #print('self.clip_img_thresh', self.clip_img_thresh)
                    #print("clip_sim_0", clip_sim_0)
                    #print("clip_sim_1", clip_sim_1[ix])
                    #print('self.clip_thresh', self.clip_thresh)
                    #print("clip_sim_dir", clip_sim_dir[ix])
                    #print("best_sim_dir", best_sim_dir[ix])
                    #print('self.clip_dir_thresh', self.clip_dir_thresh)
                    #print("prediction_is_consistent", prediction_is_consistent)
                           
                    if (
                        clip_sim_image[ix]
                        >= self.clip_img_thresh  # image-image similarity
                        and clip_sim_0 >= self.clip_thresh  # image-text similarity
                        and clip_sim_1[ix] >= self.clip_thresh  # image-text similarity
                        and clip_sim_dir[ix]
                        >= self.clip_dir_thresh  # clip directional similarity
                        and clip_sim_dir[ix] > best_sim_dir[ix]  # clip directional similarity
                        and prediction_is_consistent
                    ):
                        
                        best_sim_dir[ix] = clip_sim_dir[ix]
                        edited_image = Image.fromarray(images[ix + 1])
                        full_out_path = os.path.splitext(out_path)[
                            0
                        ] + "/{}.jpeg".format(
                            str("_".join(edits[ix].split(" "))),
                        )
                        full_out_path_diff = os.path.splitext(out_path)[
                            0
                        ] + "/{}_diff.jpeg".format(
                            str("_".join(edits[ix].split(" "))),
                        )
                        edited_image.save(full_out_path)
                        diff_image = Image.fromarray(images[ix + 1] - images[0])
                        diff_image.save(full_out_path_diff)
                        
                        prompt_dict["edits"][full_out_path] = {
                            "edited_caption": edited_caps[ix],
                            "original": originals[ix],
                            "edit": edits[ix],
                            #"edit_type": edit_types[ix],
                        }
                        if self.verbose:
                            logger.info(
                                f"Saved edited images to {os.path.splitext(out_path)[0]}\t"
                            )
                    else:
                        if self.verbose:
                            logger.info(
                                f"Edit did not meet quality thresholds, skipping\t"
                            )
        # Save prompt dict
        with open(os.path.splitext(out_path)[0] + "/prompt_dict.json", "w") as f:
            json.dump(prompt_dict, f, indent=4)


if __name__ == "__main__":
    
    args = argparse.Namespace(
        image_path="/usr/local/data/amarkr/lgcig/outputs/radedit_compare/og_image.png",
        original_caption="chest xray of a patient without support devices",
        out_path="outputs",
        save_inversion=True,
        ldm_type="finetuned_chexpert",
        edit_word_weight=2.0,
        clip_img_thresh=-0.5,
        clip_thresh=-0.5,
        clip_dir_thresh=-0.5,
    )
    accelerator = Accelerator()
    VERBOSE = True
    if VERBOSE:
        logger = get_logger(__name__)

    image_editor = ImageEditor(
        args,
        device=accelerator.device,
        text_similarity_threshold=0.9,
        ldm_type=args.ldm_type,
        verbose=VERBOSE,
        self_replace_steps_range=[0.5],
    )
    edit_path = os.path.join(args.out_path, "radedit_compare", "edited_add")
    os.makedirs(edit_path, exist_ok=True)
    _, _, x_t, uncond_embeddings = image_editor.invert(
        args.image_path, args.original_caption, os.path.join(args.out_path,"radedit_compare")
    )

    image_editor.edit(
        edit_path,
        "medical",
        x_t,
        uncond_embeddings,
        args.original_caption,
        [
            {
                "original_caption": args.original_caption,
                "edited_caption": "chest xray of a patient with cardiomegaly and support devices",
                "original": "no_dev",
                "edit": "without",
            },
            
        ],
    )
        
   