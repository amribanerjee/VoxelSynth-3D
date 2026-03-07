import numpy as np
import matplotlib.pyplot as plt
import os

# Load the volumes
base_path = "/content/processed_data"
v_phi = np.load(os.path.join(base_path, "patient1_phi.npy"))
v_final = np.load(os.path.join(base_path, "patient1_final.npy"))

# Select a slice with high artifact density (e.g., middle of the volume)
slice_idx = 330 

# Calculate the absolute difference (The "Audit" in visual form)
diff_map = np.abs(v_final[slice_idx] - v_phi[slice_idx])

# Visualization
plt.figure(figsize=(15, 5))

# 1. The Original Corrupted Slice
plt.subplot(1, 3, 1)
plt.imshow(v_phi[slice_idx], cmap='gray', vmin=-200, vmax=500)
plt.title("Baseline (with Artifacts)")
plt.axis('off')

# 2. The Corrected Slice
plt.subplot(1, 3, 2)
plt.imshow(v_final[slice_idx], cmap='gray', vmin=-200, vmax=500)
plt.title("VoxelSynth-3D Final")
plt.axis('off')

# 3. The Difference Map (The Audit Heatmap)
plt.subplot(1, 3, 3)
plt.imshow(diff_map, cmap='hot')
plt.colorbar(label='HU Shift Magnitude')
plt.title("Correction Heatmap")
plt.axis('off')

plt.tight_layout()
plt.show()
