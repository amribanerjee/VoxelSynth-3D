import numpy as np
from scipy.ndimage import sobel
from pathlib import Path
import os

class ArtifactSegmenter:
    def __init__(self, threshold_hu=2000, gradient_threshold=500):
        # Deterministic thresholds for Metal Artifacts
        self.threshold_hu = threshold_hu
        self.gradient_threshold = gradient_threshold

    def compute_3d_gradient(self, volume):
        # Equation 3: Calculating the L2 norm of the 3D Gradient
        dx = sobel(volume, axis=0)
        dy = sobel(volume, axis=1)
        dz = sobel(volume, axis=2)
        magnitude = np.sqrt(dx**2 + dy**2 + dz**2)
        return magnitude

    def generate_mask(self, volume):
        # Equation 4: Deterministic Masking (Omega)
        # Identify high-intensity metal AND high-frequency streak gradients
        grad_mag = self.compute_3d_gradient(volume)
        
        mask = np.zeros_like(volume, dtype=np.uint8)
        # Logic: V > 2000 HU (Metal) OR Gradient > Threshold (Streaks)
        mask[(volume > self.threshold_hu) | (grad_mag > self.gradient_threshold)] = 1
        
        return mask

if __name__ == "__main__":
    # Colab Paths
    phi_path = "/content/processed_data/patient1_phi.npy"
    out_dir = "/content/processed_data"
    
    if not os.path.exists(phi_path):
        print(f"Error: Could not find {phi_path}. Run preprocessing first.")
    else:
        print("Loading Isotropic Volume...")
        v_iso = np.load(phi_path)
        
        segmenter = ArtifactSegmenter()
        print("Calculating 3D Gradients and Generating Mask (Omega)...")
        
        omega_mask = segmenter.generate_mask(v_iso)
        
        # Save as patient1_mask.npy
        save_path = os.path.join(out_dir, "patient1_mask.npy")
        np.save(save_path, omega_mask)
        
        print("-" * 30)
        print(f"SUCCESS: Mask saved to {save_path}")
        print(f"Mask Shape: {omega_mask.shape} (Matches V_iso)")
        print(f"Artifact Voxel Count: {np.sum(omega_mask):,}")
        print("-" * 30)
