import numpy as np
from pathlib import Path
from scipy.ndimage import gaussian_filter

class VolumeSynthesizer:
    def __init__(self, sigma=1.5):
        self.sigma = sigma

    def volumetric_prior_fill(self, volume):
        return gaussian_filter(volume, sigma=self.sigma)

    def synthesize_final(self, original_vol, processed_vol, mask):
        return np.where(mask == 1, processed_vol, original_vol)

if __name__ == "__main__":
    base_dir = Path(__file__).parent.parent
    proc_dir = base_dir / 'data' / 'processed'
    
    synthesizer = VolumeSynthesizer(sigma=1.2)
    
    for phi_file in proc_dir.glob("*_phi.npy"):
        mask_file = phi_file.with_name(phi_file.stem.replace("_phi", "_mask") + ".npy")
        
        if mask_file.exists():
            vol = np.load(phi_file)
            mask = np.load(mask_file)
            
            prior_vol = synthesizer.volumetric_prior_fill(vol)
            final_output = synthesizer.synthesize_final(vol, prior_vol, mask)
            
            output_path = phi_file.with_name(phi_file.stem.replace("_phi", "_final") + ".npy")
            np.save(output_path, final_output)
            print(f"3D Volumetric Synthesis complete: {phi_file.name}")
