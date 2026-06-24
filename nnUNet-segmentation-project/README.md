# Hippocampus Segmentation and Volumetric Analysis

This subproject contains nnU-Net v2 helpers for a Medical Segmentation
Decathlon (MSD) hippocampus workflow. It is reference material related to, but
separate from, the main OASIS 29-ROI pipeline.

## Contents

```text
.
|-- metrics.py                         # Absolute volume and ratio calculator
|-- requirements.txt                  # Python dependencies
`-- scripts/
    |-- convert_msd_to_nnunet.py       # Dataset JSON/conversion scaffold
    |-- train_model.py                 # Python training entry point
    |-- run_train.sh                   # Bash preprocessing/training workflow
    `-- run_inference.sh               # Bash inference workflow
```

## Setup

From the repository root:

```bash
pip install -r nnUNet-segmentation-project/requirements.txt
cd nnUNet-segmentation-project
```

Set the standard nnU-Net directories for your environment:

```bash
export nnUNet_raw=/path/to/nnUNet_raw
export nnUNet_preprocessed=/path/to/nnUNet_preprocessed
export nnUNet_results=/path/to/nnUNet_results
```

## Training and inference

The included scripts use dataset ID `501` and the `3d_fullres` configuration by
default. Review all paths and dataset settings before running them.

```bash
bash scripts/run_train.sh
bash scripts/run_inference.sh
```

Alternatively, start training through Python:

```bash
python scripts/train_model.py --dataset_id 501 --configuration 3d_fullres --fold 0
```

> [!IMPORTANT]
> `scripts/convert_msd_to_nnunet.py` is a scaffold: its file-copy and filename
> conversion logic must be adapted to the source dataset before use.

## Volume utility

`metrics.py` computes an ROI's voxel count and physical volume using NIfTI voxel
spacing. When a reference mask is supplied, it also reports a percentage ratio.

```python
from metrics import BrainVolumeCalculator

calculator = BrainVolumeCalculator(target_label_idx=1)
result = calculator.calculate("data/predictions/hippocampus_001.nii.gz")
print(result["absolute_volume_mm3"])
```

This physical-volume calculation is distinct from the dimensionless OASIS
voxel-ratio feature documented in the main project README.
