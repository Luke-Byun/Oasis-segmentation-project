# Dashboard Guide (How to read this dashboard)

## What this dashboard shows
이 대시보드는 MRI Segmentation 결과로부터 계산한 **ROI별 상대 용적 비율(ratio)**과,
그 값을 입력으로 하는 **CN vs Disease(AD+MCI)** 이진 분류 모델의 출력(예측/확률)을 함께 보여줍니다.

## Key terms
- ROI ratio: 특정 ROI 라벨 voxel 수 / (label>0 전체 voxel 수)
- Total_Voxels: label>0 전체 voxel 수 (배경 제외). 절대 용적(mm³)이 아니라 voxel 개수 기반입니다.
- Disease probability: 모델이 Disease(AD+MCI)로 분류할 확률(신뢰도)이며 임상적 확진이 아닙니다.

## How to interpret ratios
- ratio는 **상대 비율**입니다. (절대 용적 아님)
- 정상 레퍼런스(z-score/percentile)가 없으면 “정상보다 크다/작다” 같은 비교를 단정할 수 없습니다.
- `tissue_like`(조직)와 `fluid_space`(뇌실/CSF)는 성격이 달라 같은 방식으로 해석하면 안 됩니다.

## QC (Quality Check)
- ratio_sum ≈ 1: 라벨 1~29가 전체(label>0)를 잘 덮었는지 확인하는 체크입니다.
- ratio_sum_error가 크면: 라벨 누락/추가, 파싱 오류, segmentation 산출물 문제 가능성이 있습니다.

## Safety note
본 대시보드는 연구/보조 목적이며 임상 진단/치료 결정을 대체하지 않습니다.
