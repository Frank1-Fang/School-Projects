#!/usr/bin/env python3
# ------------------------------------------------------------
# MASt3R Pairwise Matching + 3D Reconstruction (with COLMAP poses)
# ------------------------------------------------------------
import os
import sys
import argparse
import torch
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# === 注册路径 ===
current_dir = os.path.dirname(os.path.abspath(__file__))
mast3r_root = os.path.join(current_dir, "mast3r-main")
dust3r_root = os.path.join(mast3r_root, "dust3r")
sys.path.extend([mast3r_root, dust3r_root])

from mast3r.model import AsymmetricMASt3R
from mast3r.fast_nn import fast_reciprocal_NNs
from dust3r.inference import inference
from dust3r.utils.image import load_images


# === 手动实现线性三角化 ===
def triangulate_points(K1, K2, baseline, pts1, pts2):
    """简化版DLT三角化（线性重建）"""
    R = baseline[:3, :3]
    t = baseline[:3, 3].reshape(3, 1)

    # 投影矩阵
    P1 = K1 @ np.hstack((np.eye(3), np.zeros((3, 1))))
    P2 = K2 @ np.hstack((R, t))

    pts_3d = []
    for i in range(len(pts1)):
        x1, y1 = pts1[i]
        x2, y2 = pts2[i]
        A = np.array([
            x1 * P1[2] - P1[0],
            y1 * P1[2] - P1[1],
            x2 * P2[2] - P2[0],
            y2 * P2[2] - P2[1]
        ])
        _, _, V = np.linalg.svd(A)
        X = V[-1]
        X /= X[3]
        pts_3d.append(X[:3])
    return np.array(pts_3d, dtype=np.float32)


# === 三视图可视化 ===
def visualize_pointcloud(points3d, output_dir, prefix="mast3r_recon"):
    valid = np.isfinite(points3d).all(axis=1)
    points3d = points3d[valid]
    print(f"[INFO] Visualizing {len(points3d)} valid 3D points...")

    projections = [
        ("xy", (0, 1, 2), "Top view (XY-plane)"),
        ("xz", (0, 2, 1), "Side view (XZ-plane)"),
        ("yz", (1, 2, 0), "Front view (YZ-plane)"),
    ]

    for tag, (a, b, c), title in projections:
        fig, ax = plt.subplots(figsize=(6, 6))
        sc = ax.scatter(points3d[:, a], points3d[:, b],
                        s=1.0, c=points3d[:, c],
                        cmap="viridis", alpha=0.7)
        plt.colorbar(sc, ax=ax, fraction=0.046, pad=0.04)
        ax.set_title(f"MASt3R 3D Reconstruction - {title}")
        ax.set_xlabel(["X", "Y", "Z"][a])
        ax.set_ylabel(["X", "Y", "Z"][b])
        ax.axis("equal")
        plt.tight_layout()
        save_path = os.path.join(output_dir, f"{prefix}_{tag}.png")
        plt.savefig(save_path, dpi=300)
        plt.close(fig)
        print(f"[SAVED] {title} -> {save_path}")

    # === 三维透视视图 ===
    fig = plt.figure(figsize=(8, 6))
    ax = fig.add_subplot(111, projection='3d')
    ax.scatter(points3d[:, 0], points3d[:, 1], points3d[:, 2],
               s=0.4, c='royalblue', alpha=0.7)
    ax.set_title('MASt3R 3D Reconstruction (Perspective)')
    ax.set_xlabel('X'); ax.set_ylabel('Y'); ax.set_zlabel('Z')
    ax.view_init(elev=25, azim=45)
    plt.tight_layout()
    save_path = os.path.join(output_dir, f"{prefix}_3d.png")
    plt.savefig(save_path, dpi=300)
    plt.close(fig)
    print(f"[SAVED] Perspective view -> {save_path}")


# === 自动解析 COLMAP 相机参数与位姿 ===
def parse_colmap_cameras(camera_txt_path):
    cameras = {}
    with open(camera_txt_path, "r") as f:
        for line in f:
            if line.startswith("#") or len(line.strip()) == 0:
                continue
            elems = line.strip().split()
            cam_id = int(elems[0])
            model = elems[1]
            width, height = map(int, elems[2:4])
            params = list(map(float, elems[4:]))
            f, cx, cy = params[:3]
            K = np.array([[f, 0, cx], [0, f, cy], [0, 0, 1]], dtype=np.float32)
            cameras[cam_id] = K
    print(f"[INFO] Loaded {len(cameras)} cameras from {camera_txt_path}")
    return cameras


def parse_colmap_images(images_txt_path):
    poses = {}
    with open(images_txt_path, "r") as f:
        lines = [l.strip() for l in f.readlines() if len(l.strip()) > 0 and not l.startswith("#")]
    for i in range(0, len(lines), 2):  # 每两行一个图像
        elems = lines[i].split()
        img_id = int(elems[0])
        qw, qx, qy, qz = map(float, elems[1:5])
        tx, ty, tz = map(float, elems[5:8])
        name = elems[9]

        # 四元数转旋转矩阵
        q = np.array([qw, qx, qy, qz], dtype=np.float64)
        R = quat_to_rotmat(q)
        t = np.array([tx, ty, tz], dtype=np.float64)
        poses[name] = (R, t)
    print(f"[INFO] Loaded {len(poses)} poses from {images_txt_path}")
    return poses


def quat_to_rotmat(q):
    """四元数转旋转矩阵"""
    qw, qx, qy, qz = q
    R = np.array([
        [1 - 2*(qy**2 + qz**2), 2*(qx*qy - qz*qw),     2*(qx*qz + qy*qw)],
        [2*(qx*qy + qz*qw),     1 - 2*(qx**2 + qz**2), 2*(qy*qz - qx*qw)],
        [2*(qx*qz - qy*qw),     2*(qy*qz + qx*qw),     1 - 2*(qx**2 + qy**2)]
    ], dtype=np.float64)
    return R


def main():
    parser = argparse.ArgumentParser(description="MASt3R pairwise matching + 3D reconstruction")
    parser.add_argument("--img1", required=True, help="Path to first image")
    parser.add_argument("--img2", required=True, help="Path to second image")
    parser.add_argument("--ckpt", required=True, help="Path to MASt3R checkpoint (.pth)")
    parser.add_argument("--output", required=True, help="Output directory")
    parser.add_argument("--colmap_dir", required=True, help="Path to COLMAP sparse_txt folder")
    parser.add_argument("--size", type=int, default=512, help="Resize input images (default: 512)")
    args = parser.parse_args()

    os.makedirs(args.output, exist_ok=True)
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"[INFO] Using device: {device}")

    # === 加载 MASt3R 模型 ===
    print(f"[INFO] Loading MASt3R from checkpoint: {args.ckpt}")
    model = AsymmetricMASt3R.from_pretrained(args.ckpt).to(device).eval()

    # === 加载图像 ===
    images = load_images([args.img1, args.img2], size=args.size)
    output = inference([tuple(images)], model, device, batch_size=1, verbose=False)

    view1, pred1 = output['view1'], output['pred1']
    view2, pred2 = output['view2'], output['pred2']
    desc1, desc2 = pred1['desc'].squeeze(0).detach(), pred2['desc'].squeeze(0).detach()

    # === 匹配 ===
    matches_im0, matches_im1 = fast_reciprocal_NNs(
        desc1, desc2, subsample_or_initxy1=8,
        device=device, dist='dot', block_size=2**13
    )

    H0, W0 = map(int, view1['true_shape'][0])
    if isinstance(matches_im0, torch.Tensor): matches_im0 = matches_im0.cpu().numpy()
    if isinstance(matches_im1, torch.Tensor): matches_im1 = matches_im1.cpu().numpy()
    valid = (
        (matches_im0[:, 0] >= 3) & (matches_im0[:, 0] < W0 - 3) &
        (matches_im0[:, 1] >= 3) & (matches_im1[:, 0] >= 3)
    )
    matches_im0, matches_im1 = matches_im0[valid], matches_im1[valid]
    print(f"[INFO] Found {len(matches_im0)} valid correspondences")

    # === 加载 COLMAP 参数 ===
    cameras = parse_colmap_cameras(os.path.join(args.colmap_dir, "cameras.txt"))
    poses = parse_colmap_images(os.path.join(args.colmap_dir, "images.txt"))

    img1_name = os.path.basename(args.img1)
    img2_name = os.path.basename(args.img2)

    # 选择与图像对应的相机
    cam_ids = sorted(list(cameras.keys()))
    K1, K2 = cameras[cam_ids[0]], cameras[cam_ids[1]]
    R1, t1 = poses[img1_name]
    R2, t2 = poses[img2_name]

    # baseline = [R|t] 相对变换（2相对1）
    R_rel = R2 @ R1.T
    t_rel = t2 - R_rel @ t1
    baseline = np.eye(4, dtype=np.float32)
    baseline[:3, :3] = R_rel
    baseline[:3, 3] = t_rel
    print(f"[INFO] Constructed baseline from COLMAP poses:\n{baseline}")

    # === 三角化 ===
    points3d = triangulate_points(K1, K2, baseline, matches_im0, matches_im1)
    points3d *= 0.05  # 可视化缩放
    print(f"[INFO] Triangulated {len(points3d)} 3D points")

    # === 可视化 ===
    visualize_pointcloud(points3d, args.output, prefix=f"{img1_name}_{img2_name}")
    print(f"[DONE] Reconstruction completed. Results saved in {args.output}")


if __name__ == "__main__":
    main()
