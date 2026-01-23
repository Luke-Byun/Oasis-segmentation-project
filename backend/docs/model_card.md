# Model Card (CN vs Disease)

## Task
본 모델은 뇌 MRI Segmentation 결과로부터 계산된 **ROI별 상대 용적 비율(ratio)**을 입력으로 받아,
**Normal(CN)** 과 **Disease(AD+MCI)** 를 이진 분류합니다.

- Normal: CN
- Disease: AD + MCI

## Input
- ROI별 voxel count 기반 ratio
- ratio = (ROI voxel 수) / (배경 제외 전체 뇌 voxel 수)

## Output
- prediction: Normal 또는 Disease
- probability: Disease일 확률(0~1)

## Limitations / Warnings
- 본 결과는 임상적 진단/치료 결정을 대체하지 않습니다.
- segmentation 품질, 촬영 조건, 데이터 분포 차이에 영향을 받을 수 있습니다.
- 정상 레퍼런스 분포(z-score/percentile)가 없을 경우, 특정 ROI의 절대적 크기/작음을 단정하기 어렵습니다.
- 본 모델에서 Disease는 AD와 MCI를 하나로 묶은 범주이며, **AD/MCI를 구분 진단하지 않습니다.**
