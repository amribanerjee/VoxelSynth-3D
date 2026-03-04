import pydicom
import numpy as np
import os
from pathlib import Path

class CTPreprocessor:
    def __init__(self, output_base_path):
        self.output_base_path = Path(output_base_path)
        self.volume = None
        self.spacing = None

    def validate_and_load(self, patient_dir):
        files = [pydicom.dcmread(f) for f in Path(patient_dir).glob("*.dcm")]
        files.sort(key=lambda x: float(x.ImagePositionPatient[2]))
        
        self.volume = np.stack([f.pixel_array for f in files])
        return self.volume
