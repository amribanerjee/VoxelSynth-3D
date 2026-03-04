import pytest
import numpy as np
from pathlib import Path

@pytest.fixture
def processed_data_path():
    base_dir = Path(__file__).parent.parent
    return base_dir / 'data' / 'processed'

def test_volume_dimensions(processed_data_path):
    final_file = processed_data_path / "patient1_final.npy"
    if not final_file.exists():
        pytest.skip("Final processed file not found. Run the pipeline first.")
    
    volume = np.load(final_file)
    # Verify the volume is 3D and has the expected depth (266 slices)
    assert len(volume.shape) == 3
    assert volume.shape[0] == 266
    assert volume.shape[1] == 512
    assert volume.shape[2] == 512

def test_hu_values(processed_data_path):
    final_file = processed_data_path / "patient1_final.npy"
    if not final_file.exists():
        pytest.skip("Final processed file not found.")
    
    volume = np.load(final_file)
    # Check if Hounsfield Units are in a valid range (Air is -1000, Bone/Metal is >1000)
    # We use -1024 as a common CT baseline
    assert np.min(volume) >= -1025
    assert np.max(volume) <= 3071 # Standard max for most CT scanners

def test_mask_consistency(processed_data_path):
    phi_file = processed_data_path / "patient1_phi.npy"
    mask_file = processed_data_path / "patient1_mask.npy"
    
    if not (phi_file.exists() and mask_file.exists()):
        pytest.skip("Input files for consistency check not found.")
        
    phi = np.load(phi_file)
    mask = np.load(mask_file)
    
    # Ensure the mask is binary and matches the volume shape
    assert phi.shape == mask.shape
    assert set(np.unique(mask)).issubset({0, 1})
