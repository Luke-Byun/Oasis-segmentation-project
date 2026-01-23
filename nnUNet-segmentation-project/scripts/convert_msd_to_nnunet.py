import os
import shutil
from pathlib import Path
from nnunetv2.dataset_conversion.generate_dataset_json import generate_dataset_json

"""
[Usage]
MSD 데이터를 nnU-Net v2 포맷(DatasetXXX_Name)으로 변환합니다.
"""

# ================= Configuration =================
# 원본 MSD 데이터 경로 (예: Task04_Hippocampus 폴더)
SOURCE_DIR = "../data/Task04_Hippocampus"
# nnU-Net raw 데이터 저장 경로
NNUNET_RAW_DIR = "../data/nnUNet_raw"
# 데이터셋 ID와 이름 (nnU-Net 규칙: Dataset + 3자리숫자 + 이름)
DATASET_ID = 501  
DATASET_NAME = "Hippocampus_Decathlon"
# =================================================

def convert_data():
    task_name = f"Dataset{DATASET_ID:03d}_{DATASET_NAME}"
    target_dir = os.path.join(NNUNET_RAW_DIR, task_name)
    
    # 1. 폴더 생성 (imagesTr, labelsTr, imagesTs)
    os.makedirs(os.path.join(target_dir, "imagesTr"), exist_ok=True)
    os.makedirs(os.path.join(target_dir, "labelsTr"), exist_ok=True)
    os.makedirs(os.path.join(target_dir, "imagesTs"), exist_ok=True)

    print(f"📂 Converting data from {SOURCE_DIR} to {target_dir}...")

    # 2. 파일 복사 및 이름 변경 (MSD -> nnU-Net v2 규칙: case_000_0000.nii.gz)
    # 여기서는 간단히 MSD 파일명을 그대로 사용하거나 "_0000" 접미사를 붙이는 로직 필요
    # (실제 데이터 파일명에 따라 수정 필요)
    
    # 예시: MSD는 이미 4d 파일일 수 있으나, 여기서는 단순 복사 로직만 작성
    # 실제로는 nnUNetv2_convert_MSD_dataset 명령어를 쓰는 게 더 빠를 수 있음
    print("⚠️ 데이터 복사 로직은 원본 파일명 형태에 맞춰 구현이 필요합니다.")
    print(f"    참조: {SOURCE_DIR} 내부 파일들을 {target_dir}/imagesTr 로 이동")

    # 3. dataset.json 생성
    generate_dataset_json(
        str(target_dir),
        {0: "CT/MRI"},  # 채널 정보
        {"background": 0, "hippocampus": 1},  # 라벨 정보 (필요시 수정)
        num_training_cases=260,  # 실제 학습 데이터 개수 입력
        file_ending=".nii.gz"
    )
    print("✅ dataset.json created!")

if __name__ == "__main__":
    convert_data()