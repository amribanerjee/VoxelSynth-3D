import numpy as np
import nibabel as nib
import os

# 1. Load your Final 3D Model
base_path = "/content/processed_data"
final_model_path = os.path.join(base_path, "patient1_final.npy")

if not os.path.exists(final_model_path):
    print("Error: patient1_final.npy not found!")
else:
    data = np.load(final_model_path)
    
    # 2. Create the Affine Matrix
    # This tells the viewer software that each voxel is 1.0mm x 1.0mm x 1.0mm
    # This matches your Equation 1: Isotropic Mapping
    affine = np.eye(4) 
    
    # 3. Wrap the data into a NIfTI Image object
    # We cast to float32 to ensure compatibility with medical viewers
    nifti_img = nib.Nifti1Image(data.astype(np.float32), affine)
    
    # 4. Save the file for Dr. Roplekar
    save_path = os.path.join(base_path, "Patient1_VoxelSynth_3D.nii")
    nib.save(nifti_img, save_path)
    
    print("-" * 40)
    print(f"SUCCESS: 3D Model converted to NIfTI")
    print(f"File Saved: {save_path}")
    print("-" * 40)
    print("INSTRUCTIONS FOR DR. ROPLEKAR:")
    print("1. Download 'Patient1_VoxelSynth_3D.nii' from Colab.")
    print("2. Open it using 3D Slicer, RadiAnt, or any NIfTI viewer.")
    print("3. He can now scroll through the 44.8M corrected voxels in 3D.")
