#!/bin/bash

# ====================================================
# nnU-Net v2 Training Pipeline
# ====================================================

# 1. 환경 변수 설정 (데이터가 저장된 경로)
export nnUNet_raw="../data/nnUNet_raw"
export nnUNet_preprocessed="../data/nnUNet_preprocessed"
export nnUNet_results="../data/nnUNet_results"

# 데이터셋 ID (예: 501)
DATASET_ID=501
FOLD=0  # 5-fold cross validation 중 0번 fold 학습

echo "🚀 Starting nnU-Net Pipeline for Dataset ${DATASET_ID}..."

# 2. 데이터 전처리 및 계획 수립 (Plan & Preprocess)
# -c 3d_fullres : 3D Full Resolution 설정
echo "Process 1: Planning and Preprocessing..."
nnUNetv2_plan_and_preprocess -d ${DATASET_ID} --verify_dataset_integrity -c 3d_fullres

# 3. 모델 학습 (Training)
echo "Process 2: Training Model (Fold ${FOLD})..."
nnUNetv2_train ${DATASET_ID} 3d_fullres ${FOLD} --npz

echo "✅ Training Finished!"