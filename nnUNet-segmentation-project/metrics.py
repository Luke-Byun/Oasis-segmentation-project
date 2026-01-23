import os
import nibabel as nib
import numpy as np
from typing import Dict, Optional, Tuple, Union

class BrainVolumeCalculator:
    """
    3D MRI Segmentation Mask를 분석하여 부피(Volume)와 용적률(Ratio)을 계산하는 클래스입니다.
    Medical Segmentation Decathlon 데이터 및 nnU-Net 결과 처리에 최적화되어 있습니다.
    """

    def __init__(self, target_label_idx: int = 1):
        """
        Args:
            target_label_idx (int): 계산할 타겟 ROI의 라벨 번호 (기본값: 1 = Hippocampus)
        """
        self.target_label_idx = target_label_idx

    def _load_nifti(self, file_path: str) -> Tuple[np.ndarray, Tuple[float, float, float]]:
        """
        NIfTI 파일을 로드하여 데이터 배열과 Voxel 차원 정보를 반환합니다.
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"❌ 파일을 찾을 수 없습니다: {file_path}")

        img = nib.load(file_path)
        data = img.get_fdata()
        header = img.header
        
        # Voxel 사이즈 (x, y, z) mm 단위 추출
        voxel_dims = header.get_zooms()[:3]
        return data, voxel_dims

    def calculate(self, mask_path: str, reference_path: Optional[str] = None) -> Dict[str, float]:
        """
        단일 마스크 파일에 대한 부피 및 용적률을 계산합니다.

        Args:
            mask_path (str): 예측된 세그멘테이션 마스크 파일 경로 (.nii.gz)
            reference_path (str, optional): 전체 뇌 용적(TIV) 등 비율 계산을 위한 참조 마스크 경로.

        Returns:
            Dict[str, float]: 계산 결과 딕셔너리
        """
        # 1. 타겟 마스크 로드
        data, voxel_dims = self._load_nifti(mask_path)
        
        # 2. Voxel 하나의 실제 부피 계산 (mm³)
        voxel_vol_mm3 = np.prod(voxel_dims)
        
        # 3. 타겟 라벨에 해당하는 Voxel 개수 카운트
        target_voxel_count = np.sum(data == self.target_label_idx)
        
        # 4. 절대 부피 계산 (Count * Voxel Volume)
        absolute_vol = target_voxel_count * voxel_vol_mm3

        results = {
            "voxel_count": int(target_voxel_count),
            "voxel_volume_mm3": float(voxel_vol_mm3),
            "absolute_volume_mm3": float(absolute_vol)
        }

        # 5. (옵션) 용적률 계산 - 참조 마스크가 있을 경우
        if reference_path:
            ref_data, _ = self._load_nifti(reference_path)
            # 참조 마스크는 0이 아닌 모든 영역을 유효 영역으로 간주 (Total Brain Volume)
            ref_voxel_count = np.count_nonzero(ref_data)
            
            if ref_voxel_count > 0:
                ref_vol = ref_voxel_count * voxel_vol_mm3
                ratio = (absolute_vol / ref_vol) * 100
                results["reference_volume_mm3"] = float(ref_vol)
                results["volume_ratio_percent"] = float(ratio)
            else:
                results["volume_ratio_percent"] = 0.0

        return results

# ==========================================
# 테스트 실행 코드 (Main)
# ==========================================
if __name__ == "__main__":
    # 사용 예시
    # 실제 파일 경로로 변경하여 테스트해보세요.
    SAMPLE_MASK = "data/predictions/hippocampus_001.nii.gz"
    
    # 예외 처리 및 실행
    try:
        # 해마(Label 1) 부피 계산기 초기화
        calculator = BrainVolumeCalculator(target_label_idx=1)
        
        if os.path.exists(SAMPLE_MASK):
            result = calculator.calculate(SAMPLE_MASK)
            
            print(f"📊 Analysis Result: {SAMPLE_MASK}")
            print(f"   - Voxel Count: {result['voxel_count']:,}")
            print(f"   - Absolute Volume: {result['absolute_volume_mm3']:.2f} mm³")
        else:
            print(f"ℹ️ 테스트를 위해 '{SAMPLE_MASK}' 경로에 파일이 필요합니다.")
            print("   (이 파일은 모듈로 import해서 사용하기에 최적화되어 있습니다.)")
            
    except Exception as e:
        print(f"⚠️ Error: {e}")