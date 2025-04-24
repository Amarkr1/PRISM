import warnings
warnings.filterwarnings("ignore", category=FutureWarning)

import multiprocessing
import os
import torch
import pandas as pd
from pathlib import Path
from PIL import Image
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms
from accelerate import Accelerator
from diffusers import (
    StableDiffusionPipeline,
    DDPMScheduler,
    UNet2DConditionModel,
    AutoencoderKL
)
from transformers import CLIPTextModel, CLIPTokenizer
from tqdm.auto import tqdm
import argparse
import logging
from datetime import datetime
import torch.distributed as dist

# Configure logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
timestamp = datetime.now().strftime("%Y%m%d-%H%M")
file_handler = logging.FileHandler(f'out/finetune_{timestamp}.log')
file_handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

class CheXpertDataset(Dataset):
    def __init__(
        self,
        csv_file,
        image_root_path,
        tokenizer,
        size=512,
        center_crop=False,
    ):
        self.df = pd.read_csv(csv_file)
        self.image_root_path = image_root_path
        self.tokenizer = tokenizer
        self.size = size
        self.center_crop = center_crop
        
        if center_crop:
            self.transforms = transforms.Compose([
                transforms.Resize(size),
                transforms.CenterCrop(size),
                transforms.ToTensor(),
                transforms.Normalize([0.5], [0.5])
            ])
        else:
            self.transforms = transforms.Compose([
                transforms.Resize((size, size)),
                transforms.ToTensor(),
                transforms.Normalize([0.5], [0.5])
            ])
        
        self.create_captions()

    def create_captions(self):
        conditions = [
            'No Finding', 'Enlarged Cardiomediastinum', 'Cardiomegaly',
            'Lung Opacity', 'Lung Lesion', 'Edema', 'Consolidation',
            'Pneumonia', 'Atelectasis', 'Pneumothorax', 'Pleural Effusion',
            'Pleural Other', 'Fracture', 'Support Devices'
        ]
        
        captions = []
        for _, row in self.df.iterrows():
            findings = []
            for condition in conditions:
                if row[condition] == 1:
                    findings.append(condition)
            
            caption = "Chest X-ray showing " + ", ".join(findings) if findings else "Normal chest X-ray with no significant findings"
            captions.append(caption)
        
        self.df['caption'] = captions

    def __len__(self):
        return len(self.df)

    def __getitem__(self, idx):
        row = self.df.iloc[idx]
        image_path = os.path.join(self.image_root_path, row['Path'])
        caption = row['caption']

        image = Image.open(image_path).convert('RGB')
        image = self.transforms(image)

        encoding = self.tokenizer(
            caption,
            truncation=True,
            max_length=self.tokenizer.model_max_length,
            padding="max_length",
            return_tensors="pt"
        )

        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        return {
            "image": image,
            "input_ids": encoding.input_ids[0].to(device),
            "attention_mask": encoding.attention_mask[0].to(device)
        }

def train_one_epoch(
    accelerator,
    unet,
    vae,
    text_encoder,
    tokenizer,
    noise_scheduler,
    dataloader,
    optimizer,
    epoch,
    args
):
    unet.train()
    total_loss = 0
    
    for step, batch in enumerate(tqdm(dataloader, desc=f"Training epoch {epoch}")):
        with accelerator.accumulate(unet):
            latents = vae.encode(batch["image"]).latent_dist.sample()
            latents = latents * vae.config.scaling_factor

            noise = torch.randn_like(latents)
            bsz = latents.shape[0]
            timesteps = torch.randint(0, noise_scheduler.config.num_train_timesteps, (bsz,), device=latents.device)
            noisy_latents = noise_scheduler.add_noise(latents, noise, timesteps)

            encoder_hidden_states = text_encoder(batch["input_ids"])[0]

            noise_pred = unet(noisy_latents, timesteps, encoder_hidden_states).sample

            loss = torch.nn.functional.mse_loss(noise_pred, noise, reduction="none").mean()
            accelerator.backward(loss)

            if accelerator.sync_gradients:
                accelerator.clip_grad_norm_(unet.parameters(), 1.0)
            
            optimizer.step()
            optimizer.zero_grad()
            
            total_loss += loss.detach().item()

        if step % args.save_steps == 0 and epoch % args.save_epochs == 0:
            save_progress(accelerator, unet, args.output_dir, epoch, step)

    return total_loss / len(dataloader)

def save_progress(accelerator, unet, output_dir, epoch, step):
    if accelerator.is_main_process:
        save_path = os.path.join(output_dir, f"checkpoint-{epoch}-{step}")
        accelerator.save_state(save_path)

def main(args):
    if __name__ == "__main__":
        multiprocessing.set_start_method('spawn', force=True)
        dist.init_process_group(backend='nccl')
    
    accelerator = Accelerator(
        gradient_accumulation_steps=args.gradient_accumulation_steps,
        mixed_precision="fp16",
    )

    logging.basicConfig(
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
        datefmt="%m/%d/%Y %H:%M:%S",
        level=logging.INFO if dist.get_rank() == 0 else logging.WARN,
    )

    # Load models
    noise_scheduler = DDPMScheduler.from_pretrained(args.model_name_or_path, subfolder="scheduler")
    tokenizer = CLIPTokenizer.from_pretrained(args.model_name_or_path, subfolder="tokenizer")
    text_encoder = CLIPTextModel.from_pretrained(args.model_name_or_path, subfolder="text_encoder")
    vae = AutoencoderKL.from_pretrained(args.model_name_or_path, subfolder="vae")
    unet = UNet2DConditionModel.from_pretrained(args.model_name_or_path, subfolder="unet")

    # Move models to device
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    unet = unet.to(device)
    vae = vae.to(device)
    text_encoder = text_encoder.to(device)

    vae.requires_grad_(False)
    text_encoder.requires_grad_(False)

    # Setup training data
    train_dataset = CheXpertDataset(
        csv_file=args.train_data_path,
        image_root_path=args.image_root_path,
        tokenizer=tokenizer,
        size=args.resolution,
    )

    train_sampler = torch.utils.data.distributed.DistributedSampler(train_dataset)
    train_dataloader = DataLoader(
        train_dataset,
        batch_size=args.train_batch_size,
        shuffle=False,
        num_workers=args.num_workers,
        sampler=train_sampler,
        multiprocessing_context='spawn'
    )

    # Setup optimizer
    optimizer = torch.optim.AdamW(
        unet.parameters(),
        lr=args.learning_rate,
        betas=(args.adam_beta1, args.adam_beta2),
        weight_decay=args.adam_weight_decay,
        eps=args.adam_epsilon,
    )

    # Prepare for distributed training
    unet, optimizer, train_dataloader = accelerator.prepare(
        unet, optimizer, train_dataloader
    )

    # Training info
    total_batch_size = args.train_batch_size * accelerator.num_processes * args.gradient_accumulation_steps
    logger.info("***** Running training *****")
    logger.info(f"  Num examples = {len(train_dataset)}")
    logger.info(f"  Num Epochs = {args.num_train_epochs}")
    logger.info(f"  Instantaneous batch size per device = {args.train_batch_size}")
    logger.info(f"  Total train batch size = {total_batch_size}")
    logger.info(f"  Gradient Accumulation steps = {args.gradient_accumulation_steps}")

    # Training loop
    for epoch in range(args.num_train_epochs):
        train_sampler.set_epoch(epoch)
        train_loss = train_one_epoch(
            accelerator,
            unet,
            vae,
            text_encoder,
            tokenizer,
            noise_scheduler,
            train_dataloader,
            optimizer,
            epoch,
            args
        )
        
        if dist.get_rank() == 0:
            logger.info(f"Epoch {epoch}: Average loss = {train_loss}")
        
        if epoch == args.num_train_epochs - 1 and dist.get_rank() == 0:
            pipeline = StableDiffusionPipeline.from_pretrained(
                args.model_name_or_path,
                unet=accelerator.unwrap_model(unet),
                text_encoder=text_encoder,
                vae=vae,
                tokenizer=tokenizer,
                scheduler=noise_scheduler,
            )
            pipeline.save_pretrained(args.output_dir)

    dist.destroy_process_group()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fine-tune Stable Diffusion on CheXpert")
    parser.add_argument("--model_name_or_path", type=str, default="runwayml/stable-diffusion-v1-5")
    parser.add_argument("--train_data_path", type=str, default='/usr/local/faststorage/datasets/CheXpert-v1.0_512x512/finetune.csv')
    parser.add_argument("--image_root_path", type=str, default='/usr/local/faststorage/datasets/')
    parser.add_argument("--output_dir", type=str, default='/usr/local/data/amarkr/lgcig/saved_models/finetuned')
    parser.add_argument("--resolution", type=int, default=512)
    parser.add_argument("--train_batch_size", type=int, default=8)
    parser.add_argument("--num_train_epochs", type=int, default=100)
    parser.add_argument("--gradient_accumulation_steps", type=int, default=4)
    parser.add_argument("--learning_rate", type=float, default=1e-5)
    parser.add_argument("--adam_beta1", type=float, default=0.9)
    parser.add_argument("--adam_beta2", type=float, default=0.999)
    parser.add_argument("--adam_weight_decay", type=float, default=1e-2)
    parser.add_argument("--adam_epsilon", type=float, default=1e-08)
    parser.add_argument("--max_grad_norm", type=float, default=1.0)
    parser.add_argument("--num_workers", type=int, default=8)
    parser.add_argument("--save_steps", type=int, default=2500)
    parser.add_argument("--save_epochs", type=int, default=3)

    args = parser.parse_args()
    main(args)