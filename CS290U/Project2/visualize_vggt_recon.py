#!/usr/bin/env python3
# ------------------------------------------------------------
# VGGT 3D Reconstruction Visualization (from COLMAP sparse_txt)
# ------------------------------------------------------------
import os
import argparse
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


def read_points3d_txt(file_path):
    """读取 COLMAP 的 points3D.txt 文件"""
    points, colors = [], []
    with open(file_path, "r") as f:
        for line in f:
            if line.startswith("#") or len(line.strip()) == 0:
                continue
            elems = line.strip().split()
            if len(elems) < 7:
                continue
            xyz = list(map(float, elems[1:4]))
            rgb = list(map(float, elems[4:7]))
            points.append(xyz)
            colors.append(rgb)
    if len(points) == 0:
        raise ValueError(f"[ERROR] No valid 3D points found in {file_path}")
    return np.array(points), np.array(colors) / 255.0


def visualize_vggt_pointcloud(points3d, colors, output_dir, prefix="vggt_recon"):
    valid = np.isfinite(points3d).all(axis=1)
    points3d, colors = points3d[valid], colors[valid]
    print(f"[INFO] Visualizing {len(points3d)} valid 3D points...")

    projections = [
        ("xy", (0, 1, 2), "Top view (XY-plane)"),
        ("xz", (0, 2, 1), "Side view (XZ-plane)"),
        ("yz", (1, 2, 0), "Front view (YZ-plane)"),
    ]

    for tag, (a, b, c), title in projections:
        print(f"[INFO] Drawing projection: {tag}")
        fig, ax = plt.subplots(figsize=(6, 6))
        sc = ax.scatter(points3d[:, a], points3d[:, b],
                        s=1.0, c=points3d[:, c],
                        cmap="viridis", alpha=0.7)
        plt.colorbar(sc, ax=ax, fraction=0.046, pad=0.04)
        ax.set_title(f"VGGT 3D Reconstruction - {title}")
        ax.set_xlabel(["X", "Y", "Z"][a])
        ax.set_ylabel(["X", "Y", "Z"][b])
        ax.axis("equal")
        plt.tight_layout()
        save_path = os.path.join(output_dir, f"{prefix}_{tag}.png")
        plt.savefig(save_path, dpi=300)
        plt.close(fig)
        print(f"[SAVED] {title} -> {save_path}")

    print("[INFO] Drawing 3D perspective view...")
    fig = plt.figure(figsize=(8, 6))
    ax = fig.add_subplot(111, projection='3d')
    ax.scatter(points3d[:, 0], points3d[:, 1], points3d[:, 2],
               s=0.4, c=colors, alpha=0.7)
    ax.set_title('VGGT 3D Reconstruction (Perspective)')
    ax.set_xlabel('X'); ax.set_ylabel('Y'); ax.set_zlabel('Z')
    ax.view_init(elev=25, azim=45)
    plt.tight_layout()
    save_path = os.path.join(output_dir, f"{prefix}_3d.png")
    plt.savefig(save_path, dpi=300)
    plt.close(fig)
    print(f"[SAVED] Perspective view -> {save_path}")


def main():
    parser = argparse.ArgumentParser(description="Visualize VGGT 3D reconstruction results")
    parser.add_argument("--sparse_dir", type=str, required=True, help="Path to sparse_txt folder")
    parser.add_argument("--save_path", type=str, required=True, help="Output directory for PNG files")
    args = parser.parse_args()

    os.makedirs(args.save_path, exist_ok=True)
    points_path = os.path.join(args.sparse_dir, "points3D.txt")

    if not os.path.exists(points_path):
        raise FileNotFoundError(f"File not found: {points_path}")

    points3d, colors = read_points3d_txt(points_path)
    prefix = os.path.basename(os.path.dirname(os.path.normpath(args.sparse_dir)))
    visualize_vggt_pointcloud(points3d, colors, args.save_path, prefix=prefix)


if __name__ == "__main__":
    main()
