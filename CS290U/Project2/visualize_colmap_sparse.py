import os
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

def read_points3d(file_path):
    """读取 COLMAP 的 points3D.txt 文件"""
    points = []
    colors = []
    with open(file_path, 'r') as f:
        for line in f:
            if line.startswith('#') or len(line.strip()) == 0:
                continue
            elems = line.strip().split()
            xyz = list(map(float, elems[1:4]))
            rgb = list(map(float, elems[4:7]))
            points.append(xyz)
            colors.append(rgb)
    return np.array(points), np.array(colors) / 255.0

def read_images(file_path):
    """读取 COLMAP 的 images.txt 文件，提取相机中心位置"""
    camera_centers = []
    with open(file_path, 'r') as f:
        for line in f:
            if line.startswith('#') or len(line.strip()) == 0:
                continue
            elems = line.strip().split()
            if len(elems) >= 10:
                qw, qx, qy, qz = map(float, elems[1:5])
                tx, ty, tz = map(float, elems[5:8])
                R = quat_to_rotmat([qw, qx, qy, qz])
                C = -R.T @ np.array([tx, ty, tz])
                camera_centers.append(C)
    return np.array(camera_centers)

def quat_to_rotmat(q):
    """四元数转旋转矩阵"""
    qw, qx, qy, qz = q
    return np.array([
        [1 - 2*(qy**2 + qz**2),     2*(qx*qy - qz*qw),     2*(qx*qz + qy*qw)],
        [2*(qx*qy + qz*qw),     1 - 2*(qx**2 + qz**2),     2*(qy*qz - qx*qw)],
        [2*(qx*qz - qy*qw),     2*(qy*qz + qx*qw),     1 - 2*(qx**2 + qy**2)]
    ])

def visualize_colmap_model(sparse_dir, output_path):
    """绘制点云与相机位置"""
    points3d_path = os.path.join(sparse_dir, "points3D.txt")
    images_path = os.path.join(sparse_dir, "images.txt")

    points, colors = read_points3d(points3d_path)
    cameras = read_images(images_path)

    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection='3d')

    # 绘制点云
    ax.scatter(points[:, 0], points[:, 2], -points[:, 1],
           c=colors, s=5, alpha=0.8, label="3D Points")

    # 绘制相机中心
    ax.scatter(cameras[:, 0], cameras[:, 2], -cameras[:, 1],
           c='blue', s=80, marker='^', label='Camera Centers')

    ax.legend()
    ax.set_xlabel('X')
    ax.set_ylabel('Z')
    ax.set_zlabel('Y (height)')
    ax.set_title('COLMAP Sparse Reconstruction')

    # 自动缩放视角
    max_range = (points.max(axis=0) - points.min(axis=0)).max() / 2.0
    mid = points.mean(axis=0)
    ax.set_xlim(mid[0] - max_range, mid[0] + max_range)
    ax.set_ylim(mid[2] - max_range, mid[2] + max_range)
    ax.set_zlim(mid[1] - max_range, mid[1] + max_range)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    print(f"Visualization saved to: {output_path}")

if __name__ == "__main__":
    sparse_dir = "colmap_models/sparse/1"
    output_path = "output/colmap/sparse_model_DSP2.png"
    visualize_colmap_model(sparse_dir, output_path)
