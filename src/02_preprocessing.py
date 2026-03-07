import pydicom
import numpy as np
from pathlib import Path
from scipy.ndimage import zoom
import os

class CTPreprocessor:
    def process_to_isotropic(self, dicom_dir):
        # 1. Force the path to be absolute for Colab
        path = Path(dicom_dir).resolve()
        files = [path / f for f in os.listdir(path) if f.lower().endswith('.dcm')]
        
        if not files:
            raise FileNotFoundError(f"No .dcm files found in {path}")
            
        slices = [pydicom.dcmread(str(f)) for f in files]
        slices.sort(key=lambda x: float(x.ImagePositionPatient[2]))
        
        # 2. Stack into 3D Volume and apply HU Scaling
        vol = np.stack([s.pixel_array for s in slices]).astype(np.float32)
        slope = getattr(slices[0], 'RescaleSlope', 1)
        intercept = getattr(slices[0], 'RescaleIntercept', 0)
        vol = vol * slope + intercept
        
        # 3. Calculate Resampling Factors
        # Audit data: [2.5, 0.902, 0.902] -> Target: [1.0, 1.0, 1.0]
        current_spacing = [
            float(slices[0].SliceThickness), 
            float(slices[0].PixelSpacing[0]), 
            float(slices[0].PixelSpacing[1])
        ]
        factors = [c/1.0 for c in current_spacing]
        
        # 4. Generate Isotropic Volume
        # This fulfills Equation 2 & 3 from your paper
        iso_vol = zoom(vol, factors, order=3)
        
        return iso_vol

if __name__ == "__main__":
    # Updated path based on your last error message
    raw_dir = "/content/patient1_dicom/patient1" 
    out_dir = "/content/processed_data"
    
    # Force create the directory and verify it exists
    if not os.path.exists(out_dir):
        os.makedirs(out_dir, exist_ok=True)

    engine = CTPreprocessor()
    
    print(f"Targeting: {raw_dir}")
    print("Resampling volume (this may take a moment)...")
    
    try:
        final_vol = engine.process_to_isotropic(raw_dir)
        
        # Use os.path.join for maximum compatibility in Colab
        save_path = os.path.join(out_dir, "patient1_phi.npy")
        
        # Save the actual array
        np.save(save_path, final_vol)
        
        if os.path.exists(save_path):
            print("-" * 30)
            print(f"SUCCESS: Volume saved to {save_path}")
            print(f"New Isotropic Shape: {final_vol.shape}")
            print("-" * 30)
        else:
            print("File save failed silently. Check disk space.")
            
    except Exception as e:
        print(f"Error: {e}")
