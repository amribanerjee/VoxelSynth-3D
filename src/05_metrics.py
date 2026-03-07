import numpy as np
import os
from skimage.metrics import structural_similarity as ssim

class VoxelMetrics:
    def calculate_correction_magnitude(self, final_vol, original_phi, mask):
        # Equation 8: Measures the intensity shift (HU) specifically in the artifact zone
        # High value = Effective Metal Removal
        diff = np.abs(final_vol - original_phi)
        masked_diff = diff[mask == 1]
        return np.mean(masked_diff) if masked_diff.size > 0 else 0

    def calculate_structural_retention(self, final_vol, original_phi):
        # Measures Anatomical Fidelity across the 3D Scalar Field
        # Target: > 0.98 (98% similarity to original bone/tissue structure)
        # CT HU Range: 4000 (-1000 to 3000)
        return ssim(original_phi, final_vol, data_range=4000)

if __name__ == "__main__":
    # Colab Paths
    base_path = "/content/processed_data"
    final_path = os.path.join(base_path, "patient1_final.npy")
    phi_path = os.path.join(base_path, "patient1_phi.npy")
    mask_path = os.path.join(base_path, "patient1_mask.npy")
    
    if not all(os.path.exists(p) for p in [final_path, phi_path, mask_path]):
        print("Error: One or more .npy files are missing. Ensure you ran all 3 steps.")
    else:
        print("Loading volumes for metric analysis...")
        v_final = np.load(final_path)
        v_phi = np.load(phi_path)
        omega = np.load(mask_path)
        
        evaluator = VoxelMetrics()
        
        magnitude = evaluator.calculate_correction_magnitude(v_final, v_phi, omega)
        retention = evaluator.calculate_structural_retention(v_final, v_phi)
        
        print("-" * 40)
        print(f"--- RESULTS FOR PATIENT 1 ---")
        print(f"Mean Correction Magnitude: {magnitude:.2f} HU")
        print(f"Structural Retention (SSIM): {retention:.4f}")
        print("-" * 40)
        
        # Interpretation for the Paper
        print("INTERPRETATION:")
        if retention > 0.95:
            print("Status: High Fidelity. The engine preserved anatomy while mitigating artifacts.")
        else:
            print("Status: Check Sigma. High smoothing may be blurring clean tissue.")
