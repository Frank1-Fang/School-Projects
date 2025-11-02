import os
import json
import numpy as np

def read_cameras(camera_path):
    """读取相机内参"""
    with open(camera_path, 'r') as f:
        for line in f:
            if line.startswith('#'):
                continue
            elems = line.strip().split()
            if len(elems) < 5:
                continue
            model, width, height = elems[1], int(elems[2]), int(elems[3])
            params = list(map(float, elems[4:]))
            f = params[0]
            cx, cy = params[1], params[2]
            K = np.array([[f, 0, cx],
                          [0, f, cy],
                          [0, 0, 1]])
            return K

def quat_to_rotmat(q):
    qw, qx, qy, qz = q
    return np.array([
        [1-2*(qy**2+qz**2), 2*(qx*qy-qz*qw), 2*(qx*qz+qy*qw)],
        [2*(qx*qy+qz*qw), 1-2*(qx**2+qz**2), 2*(qy*qz-qx*qw)],
        [2*(qx*qz-qy*qw), 2*(qy*qz+qx*qw), 1-2*(qx**2+qy**2)]
    ])

def read_images(image_path):
    """读取每张图像的位姿，只处理第一行，跳过关键点行"""
    images = {}
    with open(image_path, 'r') as f:
        lines = [l.strip() for l in f if len(l.strip()) > 0 and not l.startswith('#')]

    # 只取每两行中的第一行
    for i in range(0, len(lines), 2):
        elems = lines[i].split()
        if len(elems) < 10:
            continue
        image_id = int(elems[0])
        qw, qx, qy, qz = map(float, elems[1:5])
        tx, ty, tz = map(float, elems[5:8])
        name = elems[9]
        R = quat_to_rotmat([qw, qx, qy, qz])
        t = np.array([tx, ty, tz])
        images[name] = {'R': R, 't': t}
    return images

def compute_relative_pose(img1, img2):
    """计算相对旋转和平移"""
    R1, t1 = img1['R'], img1['t']
    R2, t2 = img2['R'], img2['t']
    R_rel = R2 @ R1.T
    t_rel = t2 - R_rel @ t1
    return R_rel, t_rel

def main():
    sparse_dir = "colmap_models/sparse/1"
    camera_path = os.path.join(sparse_dir, "cameras.txt")
    image_path = os.path.join(sparse_dir, "images.txt")

    K = read_cameras(camera_path)
    images = read_images(image_path)
    image_names = sorted(list(images.keys()))

    # 选10对图像（可手动调整策略）
    pairs = [(image_names[i], image_names[i+1]) for i in range(0, 19, 2)]

    test_data = {'pairs': []}
    for i, (im1, im2) in enumerate(pairs):
        R_rel, t_rel = compute_relative_pose(images[im1], images[im2])
        entry = {
            'pair_id': i,
            'image1': im1,
            'image2': im2,
            'K': K.tolist(),
            'R': R_rel.tolist(),
            't': t_rel.tolist()
        }
        test_data['pairs'].append(entry)

    os.makedirs("test_pairs", exist_ok=True)
    with open("test_pairs/test_data_DSP.json", "w") as f:
        json.dump(test_data, f, indent=4)

    print("Test set created: test_pairs/test_data_DSP.json")

if __name__ == "__main__":
    main()
