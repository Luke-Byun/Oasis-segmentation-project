#!/bin/bash

# ====================================================
# nnU-Net v2 Inference Pipeline
# ====================================================

export nnUNet_raw="../data/nnUNet_raw"
export nnUNet_preprocessed="../data/nnUNet_preprocessed"
export nnUNet_results="../data/nnUNet_results"

DATASET_ID=501
INPUT_FOLDER="../data/test_images"   # 예측할 이미지가 있는 폴더
OUTPUT_FOLDER="../data/predictions"  # 결과가 저장될 폴더

echo "🧠 Running Inference..."

# 폴더 생성
mkdir -p ${OUTPUT_FOLDER}

# 추론 실행
# -i: 입력, -o: 출력, -d: 데이터셋ID, -c: 설정, -f: 학습한 Fold
nnUNetv2_predict -i ${INPUT_FOLDER} -o ${OUTPUT_FOLDER} -d ${DATASET_ID} -c 3d_fullres -f 0

echo "✅ Prediction saved to ${OUTPUT_FOLDER}"