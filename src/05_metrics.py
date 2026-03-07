import numpy as np
import os
from skimage.metrics import structural_similarity as ssim

class VoxelMetrics:
    def __init__(self, data_range=4000):
        self.data_range = data_range # Standard CT range (-1000 to 3000 HU)

    def calculate_metrics(self, final_vol, original_phi, mask):
        """
        Calculates the full suite of 3D Volumetric Metrics for the paper.
        """
        # 1. Magnitude of Artifact Correction (MAC)
        # Measures the average 'cleanup' power in the artifact zone
        diff = np.abs(final_vol - original_phi)
        masked_diff = diff[mask == 1]
        mac = np.mean(masked_diff) if masked_diff.size > 0 else 0
        
        # 2. Artifact Volume (AV)
        # Total physical space corrected (in voxels/mm^3)
        av_voxels = np.sum(mask)
        
        # 3. Structural Retention (SSIM)
        # Measures how much of the original anatomy was preserved
        retention = ssim(original_phi, final_vol, data_range=self.data_range)
        
        # 4. Homogeneity Gain (HG)
        # Measures the reduction in 'jitter' or noise within the artifact zone
        std_phi = np.std(original_phi[mask == 1])
        std_final = np.std(final_vol[mask == 1])
        homogeneity_gain = ((std_phi - std_final) / std_phi) * 100 if std_phi > 0 else 0
        
        return {
            "mac": mac,
            "av": av_voxels,
            "ssim": retention,
            "hg": homogeneity_gain,
            "std_phi": std_phi,
            "std_final": std_final
        }

if __name__ == "__main__":
    # Define Colab Paths
    base_path = "/content/processed_data"
    final_path = os.path.join(base_path, "patient1_final.npy")
    phi_path = os.path.join(base_path, "patient1_phi.npy")
    mask_path = os.path.join(base_path, "patient1_mask.npy")
    
    # 1. Verify Files Exist
    if not all(os.path.exists(p) for p in [final_path, phi_path, mask_path]):
        print("CRITICAL ERROR: Data files missing. Please run synthesis.py first.")
    else:
        print("Loading 3D Volumes for Final Metric Analysis...")
        v_final = np.load(final_path)
        v_phi = np.load(phi_path)
        omega = np.load(mask_path)
        
        # 2. Run Evaluation
        evaluator = VoxelMetrics()
        results = evaluator.calculate_metrics(v_final, v_phi, omega)
        
        # 3. Formal Output for Paper / IEEE TMI Submission
        print("\n" + "="*50)
        print("         VOXELSYNTH-3D: QUANTITATIVE RESULTS         ")
        print("="*50)
        print(f"{'Metric Name':<30} | {'Value':<15}")
        print("-" * 50)
        print(f"{'Artifact Volume (AV)':<30} | {results['av']:,} voxels")
        print(f"{'Correction Magnitude (MAC)':<30} | {results['mac']:.2f} HU")
        print(f"{'Structural Retention (SSIM)':<30} | {results['ssim']:.4f}")
        print(f"{'Homogeneity Gain (HG)':<30} | {results['hg']:.2f} %")
        print("-" * 50)
        
        # 4. Final Scientific Interpretation
        print("\nSCIENTIFIC INTERPRETATION:")
        if results['ssim'] > 0.96:
            status = "EXCELLENT: High anatomical fidelity confirmed."
        elif results['ssim'] > 0.94:
            status = "GOOD: Effective artifact reduction with minor smoothing."
        else:
            status = "WARNING: Review Sigma parameters to reduce blurring."
            
        print(f"Status: {status}")
        print(f"Notes: Reduced Noise SD from {results['std_phi']:.2f} to {results['std_final']:.2f} HU.")
        print("="*50)
