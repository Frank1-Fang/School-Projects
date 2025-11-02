import os
import sys
import argparse
import torch
import numpy as np
import matplotlib.pyplot as plt

# === 路径注册 ===
sys.path.append(os.path.join(os.path.dirname(__file__), "mast3r-main"))
sys.path.append(os.path.join(os.path.dirname(__file__), "mast3r-main/dust3r"))

from mast3r.model import AsymmetricMASt3R
from mast3r.fast_nn import fast_reciprocal_NNs
import mast3r.utils.path_to_dust3r
from dust3r.inference import inference
from dust3r.utils.image import load_images


def main():
    parser = argparse.ArgumentParser(description="MASt3R pairwise matching")
    parser.add_argument("--img1", type=str, required=True, help="Path to first image")
    parser.add_argument("--img2", type=str, required=True, help="Path to second image")
    parser.add_argument("--output", type=str, default="output/s1_MASt3R", help="Output directory")
    parser.add_argument("--ckpt", type=str, default="checkpoints/mast3r_vit_large/MASt3R_ViTLarge_BaseDecoder_512_catmlpdpt_metric.pth",
                        help="Local checkpoint path")
    parser.add_argument("--size", type=int, default=512)
    args = parser.parse_args()

    os.makedirs(args.output, exist_ok=True)
    device = "cuda" if torch.cuda.is_available() else "cpu"

    # === 加载模型 ===
    print(f"[INFO] Loading MASt3R from checkpoint: {args.ckpt}")
    model = AsymmetricMASt3R.from_pretrained(args.ckpt).to(device).eval()

    # === 载入两张图 ===
    images = load_images([args.img1, args.img2], size=args.size)
    output = inference([tuple(images)], model, device, batch_size=1, verbose=False)

    # === 提取结果 ===
    view1, pred1 = output['view1'], output['pred1']
    view2, pred2 = output['view2'], output['pred2']
    desc1, desc2 = pred1['desc'].squeeze(0).detach(), pred2['desc'].squeeze(0).detach()

    # === 计算匹配 ===
    matches_im0, matches_im1 = fast_reciprocal_NNs(
        desc1, desc2, subsample_or_initxy1=8,
        device=device, dist='dot', block_size=2**13
    )

    # === 去掉边缘点（注意类型转换） ===
    H0, W0 = map(int, view1['true_shape'][0])
    H1, W1 = map(int, view2['true_shape'][0])

    if isinstance(matches_im0, torch.Tensor):
        matches_im0 = matches_im0.cpu().numpy()
    if isinstance(matches_im1, torch.Tensor):
        matches_im1 = matches_im1.cpu().numpy()

    valid = (
        (matches_im0[:, 0] >= 3) & (matches_im0[:, 0] < W0 - 3) &
        (matches_im0[:, 1] >= 3) & (matches_im0[:, 1] < H0 - 3) &
        (matches_im1[:, 0] >= 3) & (matches_im1[:, 0] < W1 - 3) &
        (matches_im1[:, 1] >= 3) & (matches_im1[:, 1] < H1 - 3)
    )
    matches_im0, matches_im1 = matches_im0[valid], matches_im1[valid]
    print(f"[INFO] Found {len(matches_im0)} valid correspondences")

    # === 保存匹配点 .npz ===
    img1_name = os.path.splitext(os.path.basename(args.img1))[0]
    img2_name = os.path.splitext(os.path.basename(args.img2))[0]
    npz_path = os.path.join(args.output, f"{img1_name}_{img2_name}_matches.npz")
    np.savez(npz_path, keypoints0=matches_im0, keypoints1=matches_im1)
    print(f"[SAVED] Match data -> {npz_path}")

    # === 可视化匹配 ===
    n_viz = min(100, len(matches_im0))
    idx = np.linspace(0, len(matches_im0) - 1, n_viz).astype(int)
    viz0, viz1 = matches_im0[idx], matches_im1[idx]

    # === 图像反归一化 (生成 RGB 图) ===
    image_mean = torch.as_tensor([0.5, 0.5, 0.5]).reshape(1, 3, 1, 1)
    image_std = torch.as_tensor([0.5, 0.5, 0.5]).reshape(1, 3, 1, 1)
    imgs_rgb = []
    for view in [view1, view2]:
        rgb = view['img'] * image_std + image_mean
        imgs_rgb.append(rgb.squeeze(0).permute(1, 2, 0).cpu().numpy())

    # === 拼接两图，中间加留白 ===
    H0, W0 = imgs_rgb[0].shape[:2]
    H1, W1 = imgs_rgb[1].shape[:2]
    gap = 20  # 中间空隙像素
    canvas = np.ones((max(H0, H1), W0 + W1 + gap, 3)) * 0.2  # 灰色背景更接近SuperGlue风格
    canvas[:H0, :W0] = imgs_rgb[0]
    canvas[:H1, W0 + gap:W0 + gap + W1] = imgs_rgb[1]

    # === 绘制匹配线 ===
    plt.figure(figsize=(14, 6))
    plt.imshow(canvas)
    plt.axis('off')
    plt.title("MASt3R Matches", fontsize=14)
    cmap = plt.get_cmap('rainbow')

    for i in range(n_viz):
        color = cmap(i / (n_viz - 1))
        x0, y0 = viz0[i]
        x1, y1 = viz1[i]
        x1_shifted = x1 + W0 + gap  # 右图坐标偏移
        plt.plot([x0, x1_shifted], [y0, y1],
                color=color, linewidth=0.8, alpha=0.9)
        plt.scatter([x0, x1_shifted], [y0, y1],
                    color=color, s=8, marker='o',
                    edgecolors='w', linewidths=0.3)

    # === 左上角信息框 ===
    plt.text(15, 20, f'MASt3R\nMatches: {len(matches_im0)}',
            fontsize=10, color='white', fontweight='bold',
            bbox=dict(facecolor='black', alpha=0.4, boxstyle='round,pad=0.3'))

    # === 保存结果 ===
    png_path = os.path.join(args.output, f"{img1_name}_{img2_name}_matches.png")
    plt.savefig(png_path, dpi=200, bbox_inches='tight', pad_inches=0)
    plt.close()
    print(f"[SAVED] Visualization -> {png_path}")



if __name__ == "__main__":
    main()
