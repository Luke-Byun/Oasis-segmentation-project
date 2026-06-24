# nnU-Net Colab training cells

This file preserves the original Google Colab-oriented training commands. It is
reference material rather than a directly executable Python module.

```python
# nnUNet 코드
#내 구글 드라이브 로드 
from google.colab import drive
drive.mount('/content/drive')
# 1. 파일을 코랩 로컬 세션으로 복사 (속도 향상을 위해 로컬에서 작업하는 것이 좋습니다)
!cp "/content/drive/MyDrive/final_dataset.zip" .

# 2. 압축 풀기
!unzip -q final_dataset.zip -d ./final_dataset

# 3. 압축 파일 삭제 (용량 확보용, 선택 사항)
!rm final_dataset.zip
# nnU-Net V2 설치
!pip install nnunetv2

#데이터 전처리
import os

os.environ['nnUNet_raw'] = "/content/nnUNet_raw"
os.environ['nnUNet_preprocessed'] = "/content/nnUNet_preprocessed"
os.environ['nnUNet_results'] = "/content/nnUNet_results"

# 관련 폴더 미리 생성
!mkdir -p /content/nnUNet_preprocessed
!mkdir -p /content/nnUNet_results

import os
import nibabel as nib
import numpy as np
from pathlib import Path
from tqdm import tqdm
import json

# 1. 경로 설정
LABELS_DIR = Path('/content/nnUNet_raw/Dataset001_BrainSeg/labelsTr')
JSON_PATH = Path('/content/nnUNet_raw/Dataset001_BrainSeg/dataset.json')

# 2. 매핑 사전 정의 (기존 ID -> 새로운 연속 ID)
# 0은 배경 그대로 두고, 나머지 번호들을 순서대로 1, 2, 3... 부여합니다.
original_labels = [2, 4, 5, 7, 8, 10, 11, 12, 13, 14, 15, 16, 17, 18, 24, 26, 28, 31, 41, 43, 44, 46, 47, 49, 50, 51, 52, 53, 54]
label_names = [
    "Left-Cerebral-White-Matter", "Left-Lateral-Ventricle", "Left-Inf-Lat-Vent", "Left-Cerebellum-White-Matter",
    "Left-Cerebellum-Cortex", "Left-Thalamus", "Left-Caudate", "Left-Putamen", "Left-Pallidum", "3rd-Ventricle",
    "4th-Ventricle", "Brain-Stem", "Left-Hippocampus", "Left-Amygdala", "CSF", "Left-Accumbens-area", "Left-VentralDC",
    "Left-choroid-plexus", "Right-Cerebral-White-Matter", "Right-Lateral-Ventricle", "Right-Inf-Lat-Vent",
    "Right-Cerebellum-White-Matter", "Right-Cerebellum-Cortex", "Right-Thalamus", "Right-Caudate", "Right-Putamen",
    "Right-Pallidum", "Right-Hippocampus", "Right-Amygdala"
]

mapping = {old: new for new, old in enumerate(original_labels, start=1)}
mapping[0] = 0  # 배경은 유지

def remap_labels():
    print("🔄 라벨 재매핑 시작 (연속된 번호로 변환 중)...")
    label_files = list(LABELS_DIR.glob('*.nii.gz'))
    
    for lbl_path in tqdm(label_files):
        img = nib.load(str(lbl_path))
        data = img.get_fdata().astype(np.int16)
        
        # 새로운 데이터 배열 생성 (효율적인 매핑)
        new_data = np.zeros_like(data)
        for old_id, new_id in mapping.items():
            new_data[data == old_id] = new_id
            
        new_img = nib.Nifti1Image(new_data, img.affine, img.header)
        nib.save(new_img, str(lbl_path))

    # 3. dataset.json 업데이트
    new_label_dict = {"background": 0}
    for name, old_id in zip(label_names, original_labels):
        new_label_dict[name] = mapping[old_id]

    with open(JSON_PATH, 'r') as f:
        ds_json = json.load(f)
    
    ds_json['labels'] = new_label_dict
    
    with open(JSON_PATH, 'w') as f:
        json.dump(ds_json, f, indent=4)
        
    print("\n✅ 모든 마스크 파일과 dataset.json이 연속된 라벨 번호로 변환되었습니다!")

remap_labels()

# 환경 변수 재설정 (필요 시)
%env nnUNet_raw=/content/nnUNet_raw
%env nnUNet_preprocessed=/content/nnUNet_preprocessed
%env nnUNet_results=/content/nnUNet_results

# 다시 전처리 시도
!nnUNetv2_plan_and_preprocess -d 1 --verify_dataset_integrity

# 2. 3D Full Resolution 모델 학습 시작 (Fold 0)
!nnUNetv2_train 1 3d_fullres 0
```
