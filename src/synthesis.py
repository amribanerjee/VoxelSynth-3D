import numpy as np
from pathlib import Path
from scipy.ndimage import distance_transform_edt

class VolumeSynthesizer:
    def __init__(self, blend_factor=0.7):
        self.blend_factor = blend_factor

    def linear_interpolation_fill(self, volume, mask):
        corrected_volume = volume.copy()
        for i in range(volume.shape[0]):
            slice_data = volume[i]
            slice_mask = mask[i]
            if np.any(slice_mask):
                valid_data = slice_data[slice_mask == 0]
                fill_val = np.median(valid_data) if valid_data.size > 0 else 0
                slice_data[slice_mask == 1] = fill_val
                corrected_volume[i] = slice_data
        return corrected_volume

    def synthesize_final(self, original_vol, processed_vol, mask):
        return np.where(mask == 1, processed_vol, original_vol)
if __name__ == "__main__":
    base_dir = Path(__file__).parent.parent
    proc_dir = base_dir / 'data' / 'processed'
    
    synthesizer = VolumeSynthesizer()
    
    for phi_file in proc_dir.glob("*_phi.npy"):
        mask_file = Path(str(phi_file).replace("_phi.npy", "_mask.npy"))
        
        if mask_file.exists():
            vol = np.load(phi_file)
            mask = np.load(mask_file)
            
            interp_vol = synthesizer.linear_interpolation_fill(vol, mask)
            final_output = synthesizer.synthesize_final(vol, interp_vol, mask)
            
            output_path = Path(str(phi_file).replace("_phi.npy", "_final.npy"))
            np.save(output_path, final_output)
            print(f"Final Synthesis complete for: {phi_file.name}")
