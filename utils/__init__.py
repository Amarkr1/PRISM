from tqdm import tqdm
import numpy as np
from sklearn.cluster import KMeans
from sklearn.metrics import pairwise_distances_argmin_min

from generate_captions import *
#from edit_captions import *
#from edit_images import *
from utils.misc_utils import *
from utils.inference_utils import predict
#import datasets.lance_imagefolder as lif
#import datasets.custom_imagefolder as cif


def generate(img_dir, out_dir, args={}, device=torch.device("cuda")):
    if not args:
        args = objectview(
            {
                "exp_id": "walkthrough",
                "dset_name": img_dir,
                "lance_path": out_dir,
                "llama_finetuned_path": "checkpoints/caption_editing/lit-llama-lora-finetuned.pth",
                "llama_pretrained_path": "checkpoints/caption_editing/lit-llama.pth",
                "llama_tokenizer_path": "checkpoints/caption_editing/tokenizer.model",
            }
        )
    os.makedirs(out_dir, exist_ok=True)
    dset = cif.CustomImageFolder(img_dir)
    dataloader = torch.utils.data.DataLoader(
        dset, batch_size=1, shuffle=True, num_workers=6
    )
    ##################################################################
    # Generate LANCE
    ##################################################################
    caption_generator = CaptionGenerator(args, device, verbose=True)
    caption_editor = CaptionEditor(args, device, verbose=True)
    image_editor = ImageEditor(
        args, device, verbose=True, similarity_metric=ClipSimilarity(device=device)
    )
    for paths, targets in tqdm(dataloader):
        # Generate caption
        img_path, clsname = paths[0], targets[0]

        print(f"=>Generating LANCE for {img_path}")

        img_name = img_path.split("/")[-1]
        cap = caption_generator.generate(img_path)

        # Edit caption
        new_caps = caption_editor.edit(cap, perturbation_type="all")

        # Invert image
        _, _, x_t, uncond_embeddings = image_editor.invert(img_path, cap, out_dir)

        # Edit image
        out_path = os.path.join(out_dir, img_name)
        image_editor.edit(
            out_path, clsname.lower(), x_t, uncond_embeddings, cap, new_caps
        )
        del x_t, uncond_embeddings

    print(f"=>Finished generating counterfactuals")

    ##########################################################


def inspect(model, out_dir, class_to_idx, device=torch.device("cuda")):
    ##################################################################
    # Analyze LANCE
    ##################################################################
    lance_dset = lif.LanceImageFolder(out_dir)
    # Load LANCE images

    df = lance_dset.df
    df = df.fillna("")
    df["Label"] = df["Label"].apply(lambda x: " ".join(x.split("_")))
    df["Prediction"] = ""
    df["Sensitivity"] = 0.0
    df["Avg. sensitivity"] = 0.0
    df["Cluster"] = 0
    df["Cluster Name"] = 0
    df["LANCE prediction"] = ""
    idx_to_class = {idx: cls for cls, idx in class_to_idx.items()}
    for ix in range(len(lance_dset)):
        img_path, lance_path, label = lance_dset[ix]
        gt_idx = class_to_idx[" ".join(label.split("_"))]
        preds, indices, scores = predict(
            model, img_path, device, idx_to_class=idx_to_class
        )
        lance_preds, lance_indices, lance_scores = predict(
            model, lance_path, device, idx_to_class=idx_to_class
        )
        df.loc[ix, "Prediction"] = preds
        df.loc[ix, "LANCE prediction"] = lance_preds

        # og, edit = df.loc[ix, "Original"], df.loc[ix, "Edit"]
        # df.loc[ix, "Modification"] = (
        # "{}\u2192{}".format(og, edit) if og != "" else "[...] + {}".format(edit)
        # )
        row_label = df.loc[ix, "Label"]
        pred = df.loc[ix, "Prediction"]
        # print(row_label, pred)
        if row_label in pred:
            df.loc[ix, "Prediction"] = pred.replace(
                row_label, "<font color='green'>" + row_label + "</font>"
            )
        lance_pred = df.loc[ix, "LANCE prediction"]
        if row_label in lance_pred:
            df.loc[ix, "LANCE prediction"] = lance_pred.replace(
                row_label, "<font color='green'>" + row_label + "</font>"
            )

        og, new = compute_diff(df.loc[ix, "Caption"], df.loc[ix, "Edited Caption"])
        if og != "":
            df.loc[ix, "Caption"] = df.loc[ix, "Caption"].replace(
                og, "<mark>" + og + "</mark>"
            )
        if new != "":
            df.loc[ix, "Edited Caption"] = df.loc[ix, "Edited Caption"].replace(
                new, "<mark>" + new + "</mark>"
            )
        # Also compute sensitivity as |p(y_{GT}|x)-p(y_{GT}|x')|

        p1 = scores[indices == gt_idx].item() if gt_idx in indices else 0
        p2 = (
            lance_scores[lance_indices == gt_idx].item()
            if gt_idx in lance_indices
            else 0
        )
        df.loc[ix, "Sensitivity"] = round(abs(p1 - p2), 2)
    return df


def cluster_class_edits(df, device=torch.device("cuda")):
    classes = df["Label"].unique()
    for cls in classes:
        print(f"=>Clustering edits for {cls}")
        cls_df = df[df["Label"] == cls]
        sim_model = ClipSimilarity(device=device)
        _, feats1, feats2 = sim_model.text_similarity(
            cls_df["Edited Caption"].tolist(),
            cls_df["Caption"].tolist(),
            get_feats=True,
            lemmatize=False,
        )
        dist_feats = (feats1 - feats2).squeeze().cpu().detach().numpy()
        kmeans = KMeans(n_clusters=10, random_state=0, n_init="auto").fit(dist_feats)
        closest, _ = pairwise_distances_argmin_min(kmeans.cluster_centers_, dist_feats)
        for lab in np.unique(kmeans.labels_):
            ixs = [
                cls_df.index[ix]
                for ix in range(len(kmeans.labels_))
                if kmeans.labels_[ix] == lab
            ]
            reward = 0
            for ix in ixs:
                reward += cls_df.loc[ix, "Sensitivity"]
                cls_df.loc[ix, "Cluster"] = lab
                cls_df.loc[ix, "Cluster Name"] = cls_df.loc[
                    cls_df.index[closest[lab]], "Edit"
                ]

            avg_reward = reward / len(ixs)
            for ix in ixs:
                cls_df.loc[ix, "Avg. sensitivity"] = avg_reward
        df.loc[cls_df.index] = cls_df
    return df