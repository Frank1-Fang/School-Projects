#!/usr/bin/env python3
import os
import sys
import argparse
import numpy as np
import cv2
import pandas as pd
from glob import glob

def compute_fundamental_metrics(pts0, pts1, threshold=1.0):
    """Evaluate RANSAC-based geometric consistency."""
    # --- 基本过滤 ---
    if pts0 is None or pts1 is None:
        return np.nan, np.nan, 0
    if len(pts0) < 8 or len(pts1) < 8:
        return np.nan, np.nan, 0
    if pts0.shape[0] != pts1.shape[0]:
        n = min(len(pts0), len(pts1))
        pts0, pts1 = pts0[:n], pts1[:n]

    # --- 去掉 NaN ---
    valid_mask = ~np.isnan(pts0).any(axis=1) & ~np.isnan(pts1).any(axis=1)
    pts0, pts1 = pts0[valid_mask], pts1[valid_mask]
    if len(pts0) < 8:
        return np.nan, np.nan, 0

    F, mask = cv2.findFundamentalMat(
        pts0, pts1, cv2.FM_RANSAC, ransacReprojThreshold=threshold, confidence=0.99
    )
    if F is None or mask is None:
        return np.nan, np.nan, 0

    inlier_ratio = float(np.mean(mask))
    inlier_pts0, inlier_pts1 = pts0[mask.ravel() == 1], pts1[mask.ravel() == 1]

    # Epipolar error
    epi_errors = []
    for x1, x2 in zip(inlier_pts0, inlier_pts1):
        x1_h = np.array([x1[0], x1[1], 1.0])
        x2_h = np.array([x2[0], x2[1], 1.0])
        err = abs(np.dot(x2_h, F @ x1_h))
        epi_errors.append(err)
    mean_epi_err = np.mean(epi_errors) if len(epi_errors) > 0 else np.nan
    return inlier_ratio, mean_epi_err, len(inlier_pts0)


def evaluate_folder(folder):
    npz_files = sorted(glob(os.path.join(folder, "*.npz")))
    results = []

    for path in npz_files:
        try:
            data = np.load(path)
        except:
            print(f"[WARN] Failed to load {path}")
            continue

        pts0 = data.get("keypoints0", None)
        pts1 = data.get("keypoints1", None)
        if pts0 is None or pts1 is None:
            print(f"[WARN] {os.path.basename(path)} missing keypoints.")
            continue

        num_matches = len(pts0)
        inlier_ratio, mean_epi_err, num_inliers = compute_fundamental_metrics(pts0, pts1)

        results.append({
            "file": os.path.basename(path),
            "matches": num_matches,
            "inliers": num_inliers,
            "inlier_ratio": inlier_ratio,
            "mean_epi_error": mean_epi_err
        })

    if not results:
        print("[INFO] No valid .npz files found.")
        return None

    df = pd.DataFrame(results)
    df["method"] = os.path.basename(os.path.normpath(folder))
    df.to_csv(os.path.join(folder, "evaluation_results.csv"), index=False)

    with open(os.path.join(folder, "evaluation_summary.txt"), "w") as f:
        f.write(f"=== Evaluation Summary: {folder} ===\n")
        f.write(df.describe().to_string())
        f.write("\n\nAverage metrics:\n")
        f.write(f"Mean matches: {df['matches'].mean():.1f}\n")
        f.write(f"Mean inlier ratio: {df['inlier_ratio'].mean():.3f}\n")
        f.write(f"Mean epipolar error: {df['mean_epi_error'].mean():.3f}\n")

    print(f"[SAVED] → {os.path.join(folder, 'evaluation_results.csv')}")
    print(f"[SAVED] → {os.path.join(folder, 'evaluation_summary.txt')}")
    return df


def main():
    parser = argparse.ArgumentParser(description="Evaluate .npz matching results")
    parser.add_argument("--dir", type=str, required=True,
                        help="Directory containing .npz files")
    args = parser.parse_args()

    folder = args.dir
    if not os.path.isdir(folder):
        print(f"[ERROR] Invalid directory: {folder}")
        sys.exit(1)

    evaluate_folder(folder)


if __name__ == "__main__":
    main()
