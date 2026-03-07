import numpy as np
import os

def perform_3d_audit():
    base_path = "/content/processed_data"
    v_final = np.load(os.path.join(base_path, "patient1_final.npy"))
    v_phi = np.load(os.path.join(base_path, "patient1_phi.npy"))
    omega = np.load(os.path.join(base_path, "patient1_mask.npy"))

    print("="*50)
    print("      VOXELSYNTH-3D: VOLUMETRIC AUDIT REPORT      ")
    print("="*50)

    # 1. Integrity Check: Clean Zone (Safety Audit)
    # These are voxels where omega == 0. They should be UNTOUCHED.
    clean_mask = (omega == 0)
    diff_clean = np.abs(v_final[clean_mask] - v_phi[clean_mask])
    max_clean_drift = np.max(diff_clean)
    mean_clean_drift = np.mean(diff_clean)

    # 2. Correction Check: Artifact Zone (Efficacy Audit)
    # These are voxels where omega == 1.
    artifact_mask = (omega == 1)
    diff_art = np.abs(v_final[artifact_mask] - v_phi[artifact_mask])
    num_corrected = np.sum(diff_art > 0)

    # 3. Statistical Range Check (Clinical Audit)
    final_min, final_max = np.min(v_final), np.max(v_final)

    # OUTPUT RESULTS
    print(f"{'AUDIT CATEGORY':<25} | {'RESULT'}")
    print("-" * 50)
    print(f"{'Clean Zone Drift (Mean)':<25} | {mean_clean_drift:.6f} HU")
    print(f"{'Clean Zone Drift (Max)':<25} | {max_clean_drift:.6f} HU")
    print(f"{'Voxels Corrected':<25} | {num_corrected:,}")
    print(f"{'Final HU Range':<25} | {final_min:.1f} to {final_max:.1f}")
    print("-" * 50)

    # 4. FINAL VERDICT
    if max_clean_drift < 1e-5:
        print("VERDICT: PASS - Anatomical Integrity is 100% Preserved.")
    else:
        print("VERDICT: FAIL - Smoothing leaked into clean anatomy.")
    print("="*50)

perform_3d_audit()
