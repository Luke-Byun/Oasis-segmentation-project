# Metric Definition: Voxel-based Volume Ratio

## Definition
ROI ratio = (해당 ROI 라벨의 voxel 수) / (배경 제외 전체 뇌 voxel 수)

- 전체 뇌 voxel 수는 label > 0 조건으로 계산합니다.
- voxel spacing(mm³)은 적용하지 않습니다. (절대 용적이 아닌 상대 비율)

## Notes
- 뇌실/CSF는 조직이 아닌 공간/액체 계열이므로 조직 ROI와 동일하게 해석하지 않습니다.
- segmentation 오류 또는 촬영 조건 차이가 ratio 값에 영향을 줄 수 있습니다.
- 정상 레퍼런스 분포(z-score/percentile)가 없으면 특정 ROI가 “높다/낮다”를 단정하기 어렵습니다.

## Usage Limitation
- 본 지표는 연구 및 모델 입력 목적이며, 임상 진단 또는 치료 판단을 위한 지표가 아닙니다.
