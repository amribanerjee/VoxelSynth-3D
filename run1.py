import zipfile
import pydicom
import numpy as np
import os
import shutil
import time
import psutil
import pandas as pd
from scipy.ndimage import (zoom, gaussian_gradient_magnitude, gaussian_filter, 
                           distance_transform_edt, sobel, laplace)
from skimage.metrics import structural_similarity as ssim
from skimage.metrics import normalized_mutual_information as nmi
from skimage.morphology import binary_dilation, ball

# --- Configuration ---
DATA_PATH = 'data/raw/patient1.zip'
EXTRACT_DIR = './temp_dicom_dump'
RESULTS_CSV = 'voxelsynth_performance_metrics.csv'
ISO_RES = 1.0
METAL_HU = 1200
NUM_SEEDS = 5 

def extract_and_stack(zip_path, target_dir):
    """Step 1 & 2: DICOM ingestion and Physical Metadata Extraction."""
    if os.path.exists(target_dir):
        shutil.rmtree(target_dir)
    with zipfile.ZipFile(zip_path, 'r') as ref:
        ref.extractall(target_dir)
    
    paths = [os.path.join(r, f) for r, _, fs in os.walk(target_dir) for f in fs if f.endswith('.dcm')]
    slices = [pydicom.dcmread(p) for p in paths]
    slices.sort(key=lambda s: float(s.ImagePositionPatient[2]))
    
    # --- PHYSICAL METADATA PROFILE ---
    spacing = np.array([float(slices[0].PixelSpacing[0]), 
                        float(slices[0].PixelSpacing[1]), 
                        float(slices[0].SliceThickness)], dtype=np.float32)
    
    print(f"\n--- 🛰️ SCANNER METADATA PROFILE ---")
    print(f"Total Slices:      {len(slices)}")
    print(f"Pixel Spacing (XY): {spacing[0]:.4f} mm x {spacing[1]:.4f} mm")
    print(f"Slice Thickness (Z):{spacing[2]:.4f} mm")
    print(f"Manufacturer:      {slices[0].get('Manufacturer', 'Unknown')}")
    print(f"-----------------------------------\n")
    
    m, b = float(slices[0].RescaleSlope), float(slices[0].RescaleIntercept)
    vol_hu = (np.stack([s.pixel_array for s in slices]).astype(np.float32) * m) + b
    return vol_hu, spacing

def run_pipeline_iteration(vol_iso, mask_art, mask_donor, seed):
    """Core logic for a single seed execution (Steps 6-9)."""
    np.random.seed(seed)
    grad_mag = np.sqrt(sobel(vol_iso, axis=2)**2 + sobel(vol_iso, axis=1)**2 + sobel(vol_iso, axis=0)**2)
    
    is_streak = (mask_art > 0) & (grad_mag > (60 + np.random.uniform(-2, 2)))
    donor_pool = vol_iso[mask_donor > 0]
    fill_val = np.median(donor_pool)
    
    vol_recon = vol_iso.copy()
    vol_recon[is_streak] = (vol_iso[is_streak] * 0.1) + (fill_val * 0.9)

    weight_map = gaussian_filter(mask_art, sigma=2.5)
    v_final = (vol_recon * weight_map) + (vol_iso * (1 - weight_map))

    hu_range = np.max(vol_iso) - np.min(vol_iso)
    mse = np.mean((vol_iso - v_final)**2)
    
    return {
        'seed': seed,
        'psnr': 20 * np.log10(hu_range / np.sqrt(mse)),
        'nrmse': np.sqrt(mse) / hu_range,
        'ssim': ssim(vol_iso, v_final, data_range=hu_range),
        'mi': nmi(vol_iso, v_final),
        'epi': np.corrcoef(laplace(vol_iso).flat, laplace(v_final).flat)[0, 1],
        'lce_gain': np.std(np.diff(vol_iso, axis=0)) - np.std(np.diff(v_final, axis=0)),
        'roi_hu_error': np.mean(np.abs(vol_iso[mask_art > 0] - v_final[mask_art > 0]))
    }

def main():
    print(f"🚀 STARTING MULTI-SEED VALIDATION (N={NUM_SEEDS})...")
    vol_hu, spacing = extract_and_stack(DATA_PATH, EXTRACT_DIR)
    shutil.rmtree(EXTRACT_DIR)
    
    vol_iso = zoom(vol_hu, spacing / ISO_RES, order=3, mode='nearest')
    mask_metal = (vol_iso >= METAL_HU).astype(np.float32)
    mask_art = binary_dilation(mask_metal, ball(6)).astype(np.float32)
    mask_donor = (distance_transform_edt(1 - mask_metal) > 15).astype(np.float32)

    all_results = []
    for i in range(NUM_SEEDS):
        seed = 42 + i
        print(f"-> Executing Seed {seed}...")
        res = run_pipeline_iteration(vol_iso, mask_art, mask_donor, seed)
        all_results.append(res)

    df = pd.DataFrame(all_results)
    stats = df.agg(['mean', 'std']).transpose()
    df.to_csv(RESULTS_CSV, index=False)
    stats.to_csv('summary_statistics.csv')
    
    print(f"\n✅ STATISTICAL REPORT SAVED")
    print(stats[['mean', 'std']])

if __name__ == "__main__":
    main()
