import numpy as np
import os
from skimage.metrics import structural_similarity as ssim
from skimage.metrics import peak_signal_noise_ratio as psnr
from scipy.ndimage import laplace

class VoxelMetrics:
    def __init__(self, data_range=4000):
        self.data_range = data_range # Standard CT range (-1000 to 3000 HU)

    def calculate_metrics(self, final_vol, original_phi, mask):
        """
        Calculates the full suite of 3D Volumetric Metrics including 
        newly added PSNR, NRMSE, and EPI.
        """
        # 1. Magnitude of Artifact Correction (MAC)
        diff = np.abs(final_vol - original_phi)
        masked_diff = diff[mask == 1]
        mac = np.mean(masked_diff) if masked_diff.size > 0 else 0
        
        # 2. Structural Retention (SSIM)
        retention = ssim(original_phi, final_vol, data_range=self.data_range)

        # 3. Peak Signal-to-Noise Ratio (PSNR)
        # Added to measure the ratio between max possible power of the signal and corrupting noise
        v_psnr = psnr(original_phi, final_vol, data_range=self.data_range)

        # 4. Normalized Root Mean Square Error (NRMSE)
        # Added to provide a scale-independent measure of reconstruction error
        mse = np.mean((original_phi - final_vol) ** 2)
        nrmse = np.sqrt(mse) / (np.max(original_phi) - np.min(original_phi))

        # 5. Edge Preservation Index (EPI)
        # Measures how well high-frequency details (edges) are kept after smoothing
        # It calculates the correlation between the Laplacian of the original and the final
        lap_phi = laplace(original_phi)
        lap_final = laplace(final_vol)
        
        num = np.sum((lap_phi - np.mean(lap_phi)) * (lap_final - np.mean(lap_final)))
        den = np.sqrt(np.sum((lap_phi - np.mean(lap_phi))**2) * np.sum((lap_final - np.mean(lap_final))**2))
        epi = num / den if den != 0 else 0

        # 6. Longitudinal Continuity Error (LCE)
        # Measures the smoothness along the Z-axis (Staircase effect check)
        grad_z_final = np.abs(np.diff(final_vol, axis=2))
        lce = np.mean(grad_z_final)

        # 7. Homogeneity Gain (HG)
        std_phi = np.std(original_phi[mask == 1])
        std_final = np.std(final_vol[mask == 1])
        homogeneity_gain = ((std_phi - std_final) / std_phi) * 100 if std_phi > 0 else 0
        
        return {
            "mac": mac,
            "ssim": retention,
            "psnr": v_psnr,
            "nrmse": nrmse,
            "epi": epi,
            "lce": lce,
            "hg": homogeneity_gain,
            "std_phi": std_phi,
            "std_final": std_final
        }

if __name__ == "__main__":
    # Path logic remains the same...
    # (Assuming volumes are loaded as v_final, v_phi, omega)
    
    evaluator = VoxelMetrics()
    results = evaluator.calculate_metrics(v_final, v_phi, omega)
    
    print("\n" + "="*50)
    print(f"{'Metric Name':<30} | {'Value':<15}")
    print("-" * 50)
    print(f"{'Correction Magnitude (MAC)':<30} | {results['mac']:.2f} HU")
    print(f"{'Structural Retention (SSIM)':<30} | {results['ssim']:.4f}")
    print(f"{'Peak SNR (PSNR)':<30} | {results['psnr']:.2f} dB")
    print(f"{'Normalized RMSE (NRMSE)':<30} | {results['nrmse']:.5f}")
    print(f"{'Edge Preservation (EPI)':<30} | {results['epi']:.4f}")
    print(f"{'Longitudinal Smoothness':<30} | {results['lce']:.4f}")
    print(f"{'Homogeneity Gain (HG)':<30} | {results['hg']:.2f} %")
    print("-" * 50)
