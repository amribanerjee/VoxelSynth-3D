# Install pydicom if not already installed
!pip install pydicom

import pydicom
import numpy as np
from pathlib import Path

def audit_dicom_directory(dicom_dir):
    path = Path(dicom_dir)
    files = list(path.glob("*.dcm"))

    if not files:
        print("No DICOM files found in the directory.")
        return

    # Load all slices and sort by Z-position
    slices = [pydicom.dcmread(f) for f in files]
    slices.sort(key=lambda x: float(x.ImagePositionPatient[2]))

    # Calculate Shape
    num_slices = len(slices)
    rows = slices[0].Rows
    cols = slices[0].Columns

    # Calculate Memory (Assuming 16-bit/int16 data)
    total_voxels = num_slices * rows * cols
    memory_gb = (total_voxels * 2) / (1024**3) # 2 bytes per voxel

    # Physical Metadata (The "Physics" of your scan)
    pixel_spacing = slices[0].PixelSpacing # [x_spacing, y_spacing]
    slice_thickness = slices[0].SliceThickness if 'SliceThickness' in slices[0] else "N/A"

    print(f"--- DICOM AUDIT REPORT ---")
    print(f"Total Files Found:   {num_slices}")
    print(f"Slice Resolution:    {rows} x {cols}")
    print(f"Resulting 3D Shape:  ({num_slices}, {rows}, {cols})")
    print(f"Total Voxel Count:   {total_voxels:,}")
    print(f"Estimated RAM Load:  {memory_gb:.2f} GB")
    print(f"--- PHYSICAL PROPERTIES ---")
    print(f"Pixel Spacing (mm):  {pixel_spacing}")
    print(f"Slice Thickness (mm): {slice_thickness}")
    print(f"--------------------------")

# Usage (Update the path to your raw data folder)
audit_dicom_directory('path/to/your/raw_data')

!unzip /content/patient1.zip -d patient1_dicom

audit_dicom_directory('patient1_dicom/patient1')
