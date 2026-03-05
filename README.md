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
```
---

## 🚀 Execution Instructions

### 1. Environment Setup
Ensure you have Python 3.8+ installed. We recommend using a virtual environment to manage dependencies:
```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate

# Install required dependencies
pip install -r requirements.txt
```
### 1. Data Preparation (DICOM Workflow)
VoxelSynth-3D is designed to handle volumetric spatial data. While the engine processes data as a 3D scalar field, it accepts DICOM series as input:

* **Supported Formats:** The pipeline accepts directories containing `.dcm` files. 
* **Folder Structure:** Each scan should be in its own sub-folder within `/data/input/`.
* **Consistency:** Ensure the DICOM metadata (Slice Thickness and Spacing) is consistent across the series to maintain the integrity of the 3D scalar field.

### 2. Running the Reconstruction Pipeline
The reconstruction process follows a three-stage hybrid approach: **Segmentation** (Decision Tree), **Mapping** (Affine Geometric), and **Synthesis** (Scalar Field).

#### Standard Reconstruction (DICOM to NIfTI)
To run the full pipeline on a DICOM directory:
```bash
python main.py --input ./data/input/patient_01/ --output ./results/patient_01_reconstructed.nii.gz
```
---

## 📊 Evaluation & Benchmarking

To validate the fidelity of the reconstruction, VoxelSynth-3D includes a benchmarking suite that calculates the **Structural Similarity Index (SSIM)** and **Absolute Volumetric Error (AVE)**.



### Running Evaluation
To compare your reconstructed output against a reference ground truth:
```bash
python main.py --evaluate \
    --prediction ./results/reconstructed_vol.nii.gz \
    --ground_truth ./data/reference_vol.nii.gz
```


## 📝 Publication & Citations

This work is currently being finalized for submission to IEEE Transactions on Medical Imaging (TMI).

Title: 3D Volumetric Reconstruction via Hybrid-Operator Voxel Synthesis for Mitigation of Metal Artifacts in Computed Tomography

Authors: Amritesh Banerjee, Manal Irfan, Renil Renji Joseph, Sudeep Roplekar

Abstract
Metal artifacts in Computed Tomography (CT), arising from the dual phenomenon of photon starvation and beam hardening, present a persistent challenge to diagnostic accuracy and volumetric structural integrity. Whereas traditional two-dimensional sinogram-based interpolation methods effectively reduce slice-specific noise, they also introduce secondary artifacts and fail to maintain longitudinal continuity across the axial plane. Furthermore, purely generative deep-learning approaches usually lack the clinical traceability needed for a radiological assessment. In this study, we propose a novel three-dimensional volumetric reconstruction framework using a hybrid-operator engine to reduce photon starvation artifacts. Treating the dataset as a continuous 3D scalar field, the framework uses a multi-scale Decision Tree classification to achieve deterministic voxel segmentation within an identified artifact zone. Anatomical reconstruction is then run through affine geometric mapping, synthesizing the missing projections by leveraging high-fidelity spatial priors from adjacent unaffected regions. Experimental results across three independently reconstructed clinical datasets, confirmed against clinical ground truth, show that the three-dimensional hybrid-operator engine outperforms conventional two-dimensional methods in both Absolute Volumetric Error (AVE) and Structural Similarity Index (SSIM). This method provides a computationally efficient solution that bridges the gap between physics-centric modeling and algorithmic reconstruction, ensuring diagnostic confidence across a variety of radiological scenarios.

## 🤝 Collaboration
We are actively seeking clinical and research partners to validate the VoxelSynth-3D framework across diverse radiological scenarios.

Clinical Validation: We are looking for de-identified datasets featuring diverse metallic implants (orthopedic hardware, dental work, cardiac leads) to further test volumetric consistency.

Technical Integration: If you are interested in integrating the hybrid-operator engine into existing medical imaging pipelines, please open an issue or contact the authors directly.

