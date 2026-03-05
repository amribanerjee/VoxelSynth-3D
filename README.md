# VoxelSynth-3D
# VoxelSynth-3D: Hybrid-Operator Engine for Volumetric Metal Artifact Reduction

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Field: Medical AI](https://img.shields.io/badge/Field-Medical%20AI-red.svg)]()

**VoxelSynth-3D** is a novel 3D reconstruction framework designed to mitigate metal artifacts (photon starvation and beam hardening) in Computed Tomography (CT) data. Unlike traditional 2D sinogram interpolation, VoxelSynth-3D treats the volumetric dataset as a **continuous 3D scalar field**, ensuring longitudinal continuity and preserving structural integrity across the axial plane.

---

## 🔬 Methodology

### 1. 3D Scalar Field Representation
By treating the CT volume as a continuous scalar field, VoxelSynth-3D leverages **3D spatial priors**. This approach identifies anatomical structures that remain consistent across the $z$-axis, allowing the engine to synthesize missing data even when primary axial projections are heavily obscured by metal artifacts.



### 2. Multi-Scale Decision Tree Segmentation
We replace "black-box" deep learning with a deterministic, multi-scale Decision Tree classifier. This ensures **clinical traceability**, allowing radiologists to audit why specific voxels were flagged as artifacts based on:
* **Local Hounsfield Unit (HU) Variance**
* **Volumetric Gradient Magnitudes**
* **Physics-informed attenuation thresholds**



### 3. Affine Geometric Mapping
Anatomical reconstruction is run through **Affine Geometric Mapping**. The engine synthesizes missing projections by projecting high-fidelity spatial data from adjacent unaffected regions into the identified artifact zones, balancing physics-centric modeling with algorithmic efficiency.



---

## 📊 Performance & Validation

Validated across three independently reconstructed clinical datasets, VoxelSynth-3D demonstrates superior performance in preserving structural integrity compared to conventional methods.

| Metric | Conventional 2D MAR | VoxelSynth-3D (Ours) |
| :--- | :---: | :---: |
| **SSIM** | __ | **__** |
| **AVE** | __ | **__** |
| **Consistency** | Low (Z-axis jitter) | **High (Volumetric)** |

---

## 📁 Repository Structure

```text
├── data/                   # Clinical dataset samples
├── models/                 
│   └── decision_tree.py    # Multi-scale segmentation logic
├── src/
│   ├── hybrid_engine.py    # Main reconstruction operator
│   ├── mapping.py          # Affine geometric mapping & 3D priors
│   └── physics_utils.py    # Photon starvation & beam hardening models
├── notebooks/              # Visualization and metric plotting
└── main.py                 # Execution entry point
