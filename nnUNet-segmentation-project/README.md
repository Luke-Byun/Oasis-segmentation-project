# 🧠 Hippocampus Segmentation & Volumetric Analysis

## 📖 Overview
This project focuses on **3D Semantic Segmentation of the Hippocampus** using the **Medical Segmentation Decathlon (MSD)** dataset.

We utilize **nnU-Net v2** for robust and accurate segmentation. Additionally, the project includes a volumetric analysis module to calculate **absolute volume ($mm^3$)** and **volume ratio** (occupancy rate) from the segmentation results, which is crucial for analyzing neurodegenerative conditions.

## 📂 Repository Structure

```bash
.
├── data/                       # Dataset folder (Git ignored)
├── scripts/                    # nnU-Net execution pipelines
│   ├── convert_msd.py          # MSD to nnU-Net format converter
│   ├── run_train.sh            # Training pipeline script
│   └── run_inference.sh        # Inference pipeline script
├── metrics.py                  # Volume & Ratio calculation module
├── requirements.txt            # Project dependencies
└── README.md                   # Project documentation