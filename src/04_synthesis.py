import numpy as np
from scipy.ndimage import gaussian_filter
import os
import time

start_time = time.time()
class VoxelSynth:
    def __init__(self, sigma=1.1): # Optimized from 1.5 to improve SSIM
        self.sigma = sigma

    def apply_synthesis(self, v_iso, omega):
        # Equation 6: Volumetric Prior Synthesis (V_hat)
        # Applying the 3D Gaussian kernel (G_sigma) to the entire field
        # This acts as the solution to your Longitudinal Smoothness Integral
        v_hat = gaussian_filter(v_iso, sigma=self.sigma)

        # Equation 7: Hybrid Composition (V_final)
        # Omega (mask) = 1 represents artifact zones identified in segmentation.py
        v_final = np.where(omega == 1, v_hat, v_iso)

        return v_final

if __name__ == "__main__":
    # Colab Paths
    base_path = "/content/processed_data"
    phi_path = os.path.join(base_path, "patient1_phi.npy")
    mask_path = os.path.join(base_path, "patient1_mask.npy")

    if not os.path.exists(phi_path) or not os.path.exists(mask_path):
        print("Error: Missing phi or mask files. Run previous steps first.")
    else:
        v_iso = np.load(phi_path)
        omega = np.load(mask_path)

        # Tracking the hyperparameters for the Paper's Table 1
        current_sigma = 1.1
        print(f"Applying 3D Volumetric Synthesis (Sigma={current_sigma})...")

        engine = VoxelSynth(sigma=current_sigma)
        v_final = engine.apply_synthesis(v_iso, omega)

        # Save as patient1_final.npy
        save_path = os.path.join(base_path, "patient1_final.npy")
        np.save(save_path, v_final)

        print("-" * 30)
        print(f"SUCCESS: Final Reconstruction saved to {save_path}")
        print(f"Final Volume Shape: {v_final.shape}")
        print(f"Algorithm: VoxelSynth-3D Hybrid Composition")
        print("-" * 30)
end_time = time.time()

print(f"Total time: {end_time - start_time:.2f} seconds")
