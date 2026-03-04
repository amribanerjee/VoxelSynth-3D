import pydicom
import numpy as np
import os
from pathlib import Path
from scipy.ndimage import median_filter, zoom

class CTPreprocessor:
    def __init__(self, output_base_path):
        """
        Initializes the preprocessor with a path for saving processed volumes.
        """
        self.output_base_path = Path(output_base_path)
        self.volume = None
        self.spacing = None

    def validate_and_load(self, patient_dir):
        """
        Loads DICOM files, filters for axial slices, sorts by Z-position,
        and applies Hounsfield Unit (HU) rescaling.
        """
        # 1. Load all .dcm files and filter out scout/localizer images
        files = [pydicom.dcmread(f) for f in Path(patient_dir).glob("*.dcm")]
        files = [f for f in files if 'ImageType' in f and "AXIAL" in str(f.ImageType).upper()]
        
        if not files:
            print(f"Error: No valid axial slices found in {patient_dir}")
            return None

        # 2. Sort geometrically by the Z-axis (ImagePositionPatient[2])
        # This ensures the 266 slices are in the correct anatomical order
        files.sort(key=lambda x: float(x.ImagePositionPatient[2]))
        
        # 3. Capture physical spacing metadata (Slice Thickness, Pixel Spacing)
        self.spacing = [
            float(files[0].SliceThickness),
            float(files[0].PixelSpacing[0]),
            float(files[0].PixelSpacing[1])
        ]
        
        # 4. Stack 2D slices into a 3D volume
        self.volume = np.stack([f.pixel_array for f in files])
        
        # 5. Apply Rescale Slope and Intercept to get true Hounsfield Units (HU)
        # Using float32 keeps the 266-slice volume lightweight for 16GB RAM
        slope = files[0].RescaleSlope if 'RescaleSlope' in files[0] else 1
        intercept = files[0].RescaleIntercept if 'RescaleIntercept' in files[0] else 0
        self.volume = self.volume.astype(np.float32) * slope + intercept
        
        print(f"Volume loaded: {self.volume.shape} with spacing {self.spacing}")
        return self.volume

    def apply_transforms(self, target_spacing=[1.0, 1.0, 1.0]):
        """
        Applies 3D median filtering to reduce noise and resamples 
        the volume to be isotropic (1mm x 1mm x 1mm).
        """
        if self.volume is None:
            return None
            
        # Denoising: 3D median filter is superior for preserving metal edges
        print("Applying 3D median filter...")
        self.volume = median_filter(self.volume, size=3)
        
        # Resampling: Making voxels cubic for accurate 3D gradient calculation
        print(f"Resampling to target spacing: {target_spacing}...")
        factors = [c/t for c, t in zip(self.spacing, target_spacing)]
        self.volume = zoom(self.volume, factors, order=3)
        
        # Update spacing metadata to reflect the transformed state
        self.spacing = target_spacing
        return self.volume

    def save_volume(self, patient_id):
        """Saves the processed 3D volume as a compressed NumPy file."""
        os.makedirs(self.output_base_path, exist_ok=True)
        save_path = self.output_base_path / f"{patient_id}_phi.npy"
        np.save(save_path, self.volume)
        print(f"Success: Processed volume saved to {save_path}")

if __name__ == "__main__":
    import sys
    # Configure paths: defaults to data/raw and external_storage/processed
    raw_root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path('data/raw/')
    proc_out = Path(sys.argv[2]) if len(sys.argv) > 2 else Path('external_storage/processed/')
    
    # Initialize the engine
    engine = CTPreprocessor(output_base_path=proc_out)
    
    # Batch process all patient directories in the raw root
    if not raw_root.exists():
        print(f"Directory {raw_root} not found. Please check your data structure.")
    else:
        for patient_folder in raw_root.iterdir():
            if patient_folder.is_dir():
                print(f"\n--- Processing: {patient_folder.name} ---")
                vol = engine.validate_and_load(patient_folder)
                if vol is not None:
                    engine.apply_transforms()
                    engine.save_volume(patient_folder.name)
