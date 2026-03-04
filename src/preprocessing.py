import pydicom
import numpy as np
import os
from pathlib import Path
from scipy.ndimage import median_filter, zoom

class CTPreprocessor:
    def __init__(self, output_base_path):
        self.output_base_path = Path(output_base_path)
        self.volume = None
        self.spacing = None

    def validate_and_load(self, patient_dir):
        files = [pydicom.dcmread(f) for f in Path(patient_dir).glob("*.dcm")]
        files = [f for f in files if 'ImageType' in f and "AXIAL" in str(f.ImageType).upper()]
        
        if not files:
            return None

        files.sort(key=lambda x: float(x.ImagePositionPatient[2]))
        
        self.spacing = [
            float(files[0].SliceThickness),
            float(files[0].PixelSpacing[0]),
            float(files[0].PixelSpacing[1])
        ]
        
        self.volume = np.stack([f.pixel_array for f in files])
        
        slope = files[0].RescaleSlope if 'RescaleSlope' in files[0] else 1
        intercept = files[0].RescaleIntercept if 'RescaleIntercept' in files[0] else 0
        self.volume = self.volume.astype(np.float32) * slope + intercept
        
        return self.volume

    def apply_transforms(self, target_spacing=[1.0, 1.0, 1.0]):
        if self.volume is None:
            return None
        self.volume = median_filter(self.volume, size=3)
        factors = [c/t for c, t in zip(self.spacing, target_spacing)]
        self.volume = zoom(self.volume, factors, order=3)
        self.spacing = target_spacing
        return self.volume

    def save_volume(self, patient_id):
        os.makedirs(self.output_base_path, exist_ok=True)
        save_path = self.output_base_path / f"{patient_id}_phi.npy"
        np.save(save_path, self.volume)

if __name__ == "__main__":
    # Updated paths for VoxelSynth-3D repo structure
    base_dir = Path(__file__).parent.parent
    raw_root = base_dir / 'data' / 'raw'
    proc_out = base_dir / 'data' / 'processed'
    
    engine = CTPreprocessor(output_base_path=proc_out)
    
    if raw_root.exists():
        for patient_folder in raw_root.iterdir():
            if patient_folder.is_dir():
                vol = engine.validate_and_load(patient_folder)
                if vol is not None:
                    engine.apply_transforms()
                    engine.save_volume(patient_folder.name)
