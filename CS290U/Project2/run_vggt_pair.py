import os
import sys
import argparse
import torch
import numpy as np
import matplotlib.pyplot as plt

# === 导入 VGGT 模型 ===
sys.path.append(os.path.join(os.path.dirname(__file__), "vggt-main"))
from vggt.models.vggt import VGGT
from vggt.utils.load_fn import load_and_preprocess_images


def main():
    parser = argparse.ArgumentParser(description="VGGT pairwise matching (Scenario 1)")
    parser.add_argument("--img1", type=str, required=True, help="Path to first image")
    parser.add_argument("--img2", type=str, required=True, help="Path to second image")
    parser.add_argument("--output", type=str, default="output/vggt_pair", help="Output directory")
    parser.add_argument("--ckpt", type=str, required=True, help="Local checkpoint path (model.pt)")
    parser.add_argument("--n_points", type=int, default=200, help="Number of tracking points to visualize")
    args = parser.parse_args()

    os.makedirs(args.output, exist_ok=True)

    # === Step 1: 初始化模型 ===
    device = "cuda" if torch.cuda.is_available() else "cpu"
    cc = torch.cuda.get_device_capability() if torch.cuda.is_available() else (0, 0)
    dtype = torch.bfloat16 if cc[0] >= 8 else torch.float16

    print(f"[INFO] Loading VGGT checkpoint from: {args.ckpt}")
    model = VGGT()
    state_dict = torch.load(args.ckpt, map_location="cpu")
    model.load_state_dict(state_dict, strict=False)
    model = model.to(device).eval()

    # === Step 2: 加载两张图 ===
    image_names = [args.img1, args.img2]
    images = load_and_preprocess_images(image_names).to(device)

    # === Step 3: 提取特征 ===
    with torch.no_grad():
        with torch.cuda.amp.autocast(dtype=dtype):
            images = images.unsqueeze(0) if images.ndim == 4 else images
            agg_tokens, ps_idx = model.aggregator(images)

    # === Step 4: 随机采样第一张图中的点 ===
    H, W = images.shape[-2:]
    query_points = torch.rand((args.n_points, 2)) * torch.FloatTensor([[W, H]])
    query_points = query_points.to(device)

    with torch.no_grad():
        track_list, vis_score, conf_score = model.track_head(
            agg_tokens, images, ps_idx, query_points=query_points[None]
        )

    # === Step 5: 提取匹配点 ===
    out_tracks = track_list[0]

    # 统一形状为 [num_frames, n_points, 2]
    if out_tracks.ndim == 4:
        # e.g. [1, 2, N, 2]
        out_tracks = out_tracks.squeeze(0)

    if out_tracks.ndim == 3 and out_tracks.shape[0] >= 2:
        pts0 = out_tracks[0].cpu().numpy()
        pts1 = out_tracks[1].cpu().numpy()
    elif out_tracks.ndim == 2:
        # 单帧情况
        pts0 = query_points.cpu().numpy()
        pts1 = out_tracks.cpu().numpy()
    else:
        raise ValueError(f"Unexpected track_head output shape: {out_tracks.shape}")

    # === 过滤 NaN 匹配 ===
    if pts1.ndim == 2:
        valid_mask = np.all(~np.isnan(pts1), axis=1)
    else:
        raise ValueError(f"Invalid pts1 shape: {pts1.shape}")

    pts0, pts1 = pts0[valid_mask], pts1[valid_mask]
    print(f"[INFO] Found {len(pts0)} valid matches.")


    # === Step 6: 保存匹配点 ===
    img1_name = os.path.splitext(os.path.basename(args.img1))[0]
    img2_name = os.path.splitext(os.path.basename(args.img2))[0]
    npz_path = os.path.join(args.output, f"{img1_name}_{img2_name}_matches.npz")
    np.savez(npz_path, keypoints0=pts0, keypoints1=pts1)
    print(f"[INFO] Saved match data -> {npz_path}")

    # === Step 7: 可视化 ===
    imgs_rgb = [plt.imread(args.img1), plt.imread(args.img2)]
    H0, W0 = imgs_rgb[0].shape[:2]
    H1, W1 = imgs_rgb[1].shape[:2]
    gap = 20
    canvas = np.ones((max(H0, H1), W0 + W1 + gap, 3)) * 0.2
    canvas[:H0, :W0] = imgs_rgb[0][:H0, :W0, :3]
    canvas[:H1, W0 + gap:W0 + gap + W1] = imgs_rgb[1][:H1, :W1, :3]

    plt.figure(figsize=(14, 6))
    plt.imshow(canvas)
    plt.axis("off")
    plt.title("VGGT Matches", fontsize=14)
    cmap = plt.get_cmap("rainbow")

    for i in range(len(pts0)):
        color = cmap(i / len(pts0))
        x0, y0 = pts0[i]
        x1, y1 = pts1[i]
        plt.plot([x0, x1 + W0 + gap], [y0, y1], color=color, linewidth=0.8, alpha=0.9)
        plt.scatter([x0, x1 + W0 + gap], [y0, y1], color=color, s=8, edgecolors="w", linewidths=0.3)

    plt.text(15, 20, f"VGGT\nMatches: {len(pts0)}",
             fontsize=10, color="white", fontweight="bold",
             bbox=dict(facecolor="black", alpha=0.4, boxstyle="round,pad=0.3"))

    png_path = os.path.join(args.output, f"{img1_name}_{img2_name}_matches.png")
    plt.savefig(png_path, dpi=200, bbox_inches="tight", pad_inches=0)
    plt.close()
    print(f"[INFO] Saved visualization -> {png_path}")


if __name__ == "__main__":
    main()
