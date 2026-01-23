# 🧠 Hippocampus Segmentation & Volumetric Analysis Project

![Python](https://img.shields.io/badge/Python-3.9%2B-blue)
![PyTorch](https://img.shields.io/badge/PyTorch-2.0%2B-orange)
![nnU-Net](https://img.shields.io/badge/nnU--Net-v2-green)

## 📖 Introduction
This project aims to automate the **3D segmentation of the hippocampus** from brain MRI scans and perform **quantitative volumetric analysis**.

The hippocampus is a critical brain structure associated with memory, and its atrophy is a key biomarker for neurodegenerative diseases such as **Alzheimer's Disease (AD)**. By leveraging **nnU-Net v2** and the **Medical Segmentation Decathlon (MSD)** dataset, this project provides a robust pipeline for precise segmentation and volume calculation ($mm^3$).

## ✨ Key Features
* **State-of-the-Art Segmentation:** Utilizes **nnU-Net v2** (3D Full Resolution) for high-accuracy segmentation.
* **Automated Pipeline:** Provides both **Shell** and **Python** scripts for seamless training and inference.
* **Quantitative Analysis:** Includes a dedicated module (`metrics.py`) to calculate **Absolute Volume ($mm^3$)** and **Volume Ratio (%)**, enabling clinical interpretation of the segmentation results.

---

## 📂 Project Structure

```bash
.
├── data/                       # Dataset directory (Ignored by Git)
├── scripts/                    # Automation scripts
│   ├── convert_msd.py          # Data format converter (MSD -> nnU-Net)
│   ├── run_train.sh            # One-click training script (Shell)
│   ├── train_model.py          # Python-based training script
│   └── run_inference.sh        # Inference script for test data
├── metrics.py                  # Volumetric analysis tool (Core Logic)
├── requirements.txt            # Python dependencies
└── README.md                   # Project documentation
