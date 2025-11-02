#!/usr/bin/env python3
import os, sys
sys.path.append(os.path.join(os.path.dirname(__file__), 'SuperGluePretrainedNetwork-master'))
import cv2
import json
import argparse
import numpy as np
import torch
import pandas as pd
from pathlib import Path
from math import acos, degrees
from models.matching import Matching
from models.utils import make_matching_plot_fast, frame2tensor


torch.set_grad_enabled(False)


# === 辅助函数 ===
def rotation_error(R_gt, R_est):
    """计算旋转误差 (degrees)"""
    err = np.trace(R_gt.T @ R_est)
    err = np.clip((err - 1) / 2, -1, 1)
    return degrees(acos(err))

def translation_error(t_gt, t_est):
    """计算平移误差 (degrees)"""
    # flatten to 1D
    t_gt = t_gt.flatten()
    t_est = t_est.flatten()
    t_gt = t_gt / np.linalg.norm(t_gt)
    t_est = t_est / np.linalg.norm(t_est)
    val = np.clip(np.dot(t_gt, t_est), -1, 1)
    return degrees(acos(val))


def run_superglue_eval(json_path, input_dir, output_dir, device='cuda'):
    # === 1. 加载测试数据 ===
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    pairs = data["pairs"]
    print(f"Loaded {len(pairs)} pairs from {json_path}")

    # === 2. 初始化 SuperGlue 模型 ===
    config = {
        'superpoint': {'nms_radius': 4, 'keypoint_threshold': 0.005, 'max_keypoints': 1024},
        'superglue': {'weights': 'outdoor', 'sinkhorn_iterations': 20, 'match_threshold': 0.2},
    }
    device = 'cuda' if torch.cuda.is_available() and device == 'cuda' else 'cpu'
    print(f"Running SuperGlue on device: {device}")
    matching = Matching(config).eval().to(device)

    Path(output_dir).mkdir(parents=True, exist_ok=True)

    # === 3. 开始处理所有 pairs ===
    records = []  # 用于最终保存 CSV
    for pair in pairs:
        pair_id = pair["pair_id"]
        img1_name = pair["image1"]
        img2_name = pair["image2"]
        K = np.array(pair["K"])
        R_gt = np.array(pair["R"])
        t_gt = np.array(pair["t"]).reshape(3, 1)

        path0 = os.path.join(input_dir, img1_name)
        path1 = os.path.join(input_dir, img2_name)
        if not os.path.exists(path0) or not os.path.exists(path1):
            print(f"[!] Skipped pair {pair_id}: missing images.")
            continue

        print(f"\nProcessing pair {pair_id}: {img1_name} <-> {img2_name}")

        img0 = cv2.imread(path0, cv2.IMREAD_GRAYSCALE)
        img1 = cv2.imread(path1, cv2.IMREAD_GRAYSCALE)
        if img0 is None or img1 is None:
            print(f"[!] Failed to load images for pair {pair_id}")
            continue

        # === 3.1 SuperGlue 匹配 ===
        inp = {'image0': frame2tensor(img0, device), 'image1': frame2tensor(img1, device)}
        pred = matching(inp)

        kpts0 = pred['keypoints0'][0].cpu().numpy()
        kpts1 = pred['keypoints1'][0].cpu().numpy()
        matches = pred['matches0'][0].cpu().numpy()
        conf = pred['matching_scores0'][0].cpu().numpy()

        valid = matches > -1
        mkpts0 = kpts0[valid]
        mkpts1 = kpts1[matches[valid]]

        # === 3.2 如果匹配点太少，跳过 ===
        if len(mkpts0) < 8:
            print(f"[!] Too few matches ({len(mkpts0)}). Skipped.")
            records.append({
                "pair_id": pair_id,
                "image1": img1_name,
                "image2": img2_name,
                "num_matches": len(mkpts0),
                "rot_error_deg": np.nan,
                "trans_error_deg": np.nan
            })
            continue

        # === 3.3 估计相对姿态 ===
        E, mask = cv2.findEssentialMat(mkpts0, mkpts1, K, cv2.RANSAC, 0.999, 1.0)
        if E is None:
            print(f"[!] Failed to find Essential matrix for pair {pair_id}")
            continue
        _, R_est, t_est, _ = cv2.recoverPose(E, mkpts0, mkpts1, K)

        # === 3.4 计算误差 ===
        rot_err = rotation_error(R_gt, R_est)
        trans_err = translation_error(t_gt, t_est)
        print(f"Rotation Error: {rot_err:.2f}°, Translation Error: {trans_err:.2f}°")

        # === 3.5 保存结果 ===
        np.savez(os.path.join(output_dir, f"pair_{pair_id:03d}_matches.npz"),
                 mkpts0=mkpts0, mkpts1=mkpts1, conf=conf[valid], R_est=R_est, t_est=t_est)

        color = cv2.applyColorMap((conf[valid]*255).astype(np.uint8), cv2.COLORMAP_JET)[:, 0, :]
        out = make_matching_plot_fast(
            img0, img1, kpts0, kpts1, mkpts0, mkpts1, color,
            [f"Pair {pair_id}", f"Matches: {len(mkpts0)}", 
             f"RotErr: {rot_err:.2f}°", f"TransErr: {trans_err:.2f}°"],
            path=None)
        vis_path = os.path.join(output_dir, f"pair_{pair_id:03d}.png")
        cv2.imwrite(vis_path, out)

        records.append({
            "pair_id": pair_id,
            "image1": img1_name,
            "image2": img2_name,
            "num_matches": len(mkpts0),
            "rot_error_deg": rot_err,
            "trans_error_deg": trans_err
        })
        print(f"Saved visualization to {vis_path}")

    # === 4. 输出统计结果 ===
    df = pd.DataFrame(records)
    csv_path = os.path.join(output_dir, "evaluation_summary.csv")
    df.to_csv(csv_path, index=False)
    print(f"\nEvaluation summary saved to {csv_path}")
    print(df.describe())


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Full SuperGlue evaluation pipeline for Project 2")
    parser.add_argument("--json_path", type=str, required=True, help="Path to your test_pairs.json")
    parser.add_argument("--input_dir", type=str, required=True, help="Directory containing input images")
    parser.add_argument("--output_dir", type=str, default="results", help="Directory to save results")
    parser.add_argument("--device", type=str, default="cuda", choices=["cuda", "cpu"], help="Device for inference")

    args = parser.parse_args()
    run_superglue_eval(args.json_path, args.input_dir, args.output_dir, args.device)
