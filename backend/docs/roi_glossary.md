# ROI Glossary (Segmentation Labels)

본 문서는 분할 라벨 기반 용적/용적률 대시보드 설명을 위한 ROI 사전입니다.

⚠️ 주의: 아래 설명은 **일반적 의미**이며, 개별 환자에 대한 **진단/치료 결론을 의미하지 않습니다.**

## Label List

| label_id | roi_key | hemisphere | korean_name | type_tag | short_description |
|---:|---|:---:|---|---|---|
| 1 | L_Cerebral_WM | L | 대뇌 백질 | tissue_like | 대뇌의 신경섬유(연결)로 구성된 영역입니다. 전반적 구조/연결성과 관련된 지표로 해석될 수 있습니다. |
| 2 | L_LatVent | L | 측뇌실 | fluid_space | 뇌실은 뇌척수액이 차는 공간입니다. 조직이 아니라 '공간'이므로 해석 방식이 다릅니다. |
| 3 | L_InfLatVent | L | 하측뇌실(측뇌실 하각) | fluid_space | 뇌척수액 공간(뇌실의 일부)입니다. 조직이 아니라 공간 지표입니다. |
| 4 | L_Cb_WM | L | 소뇌 백질 | tissue_like | 소뇌 내부의 백질 영역입니다. 운동/균형 기능과 관련된 네트워크와 연관될 수 있습니다. |
| 5 | L_Cb_Ctx | L | 소뇌 피질 | tissue_like | 소뇌의 회백질(피질) 영역입니다. 운동 조절 및 일부 인지 기능과 관련될 수 있습니다. |
| 6 | L_Thalamus | L | 시상 | tissue_like | 감각/운동 정보 중계에 관여하는 심부핵입니다. |
| 7 | L_Caudate | L | 꼬리핵 | tissue_like | 기저핵의 일부로 운동/학습/인지 기능과 관련될 수 있습니다. |
| 8 | L_Putamen | L | 조가비핵 | tissue_like | 기저핵의 일부로 운동 기능과 관련될 수 있습니다. |
| 9 | L_Pallidum | L | 창백핵 | tissue_like | 기저핵 회로의 일부로 운동 조절과 관련될 수 있습니다. |
| 10 | V3 | - | 제3뇌실 | fluid_space | 뇌척수액 공간(뇌실)입니다. 조직이 아닌 공간 지표입니다. |
| 11 | V4 | - | 제4뇌실 | fluid_space | 뇌척수액 공간(뇌실)입니다. 조직이 아닌 공간 지표입니다. |
| 12 | BrainStem | - | 뇌간 | tissue_like | 생명 유지 및 신경 경로가 집중된 구조로 알려져 있습니다. |
| 13 | L_Hippocampus | L | 해마 | tissue_like | 기억 형성과 관련된 구조로 알려져 있습니다. 단, 단일 지표만으로 임상적 결론을 내리면 안 됩니다. |
| 14 | L_Amygdala | L | 편도체 | tissue_like | 정서 처리와 관련된 구조로 알려져 있습니다. |
| 15 | CSF | - | 뇌척수액(CSF) | fluid_space | 뇌척수액의 분할/추정 값입니다. 공간/액체 성격이 강해 조직과 다르게 해석해야 합니다. |
| 16 | L_Accumbens | L | 측좌핵 | tissue_like | 보상/동기 회로와 관련된 영역으로 알려져 있습니다. |
| 17 | L_VentralDC | L | Ventral Diencephalon Complex | tissue_like | 간뇌 하부 영역(시상하부 주변 등)을 포함하는 구조 묶음입니다. |
| 18 | L_ChoroidPlexus | L | 맥락총 | ventricle_related | 뇌척수액 생성과 관련된 구조입니다. 뇌실과 인접해 전처리/분할 편차의 영향을 받을 수 있습니다. |
| 19 | R_Cerebral_WM | R | 대뇌 백질 | tissue_like | 대뇌의 신경섬유(연결)로 구성된 영역입니다. 전반적 구조/연결성과 관련된 지표로 해석될 수 있습니다. |
| 20 | R_LatVent | R | 측뇌실 | fluid_space | 뇌실은 뇌척수액이 차는 공간입니다. 조직이 아니라 '공간'이므로 해석 방식이 다릅니다. |
| 21 | R_InfLatVent | R | 하측뇌실(측뇌실 하각) | fluid_space | 뇌척수액 공간(뇌실의 일부)입니다. 조직이 아니라 공간 지표입니다. |
| 22 | R_Cb_WM | R | 소뇌 백질 | tissue_like | 소뇌 내부의 백질 영역입니다. 운동/균형 기능과 관련된 네트워크와 연관될 수 있습니다. |
| 23 | R_Cb_Ctx | R | 소뇌 피질 | tissue_like | 소뇌의 회백질(피질) 영역입니다. 운동 조절 및 일부 인지 기능과 관련될 수 있습니다. |
| 24 | R_Thalamus | R | 시상 | tissue_like | 감각/운동 정보 중계에 관여하는 심부핵입니다. |
| 25 | R_Caudate | R | 꼬리핵 | tissue_like | 기저핵의 일부로 운동/학습/인지 기능과 관련될 수 있습니다. |
| 26 | R_Putamen | R | 조가비핵 | tissue_like | 기저핵의 일부로 운동 기능과 관련될 수 있습니다. |
| 27 | R_Pallidum | R | 창백핵 | tissue_like | 기저핵 회로의 일부로 운동 조절과 관련될 수 있습니다. |
| 28 | R_Hippocampus | R | 해마 | tissue_like | 기억 형성과 관련된 구조로 알려져 있습니다. 단, 단일 지표만으로 임상적 결론을 내리면 안 됩니다. |
| 29 | R_Amygdala | R | 편도체 | tissue_like | 정서 처리와 관련된 구조로 알려져 있습니다. |

## Interpretation Notes
- `tissue_like`: 조직(핵/백질/피질) 계열 ROI입니다.
- `fluid_space`: 뇌실/CSF 등 공간/액체 계열 ROI로 조직과 동일하게 해석하지 않습니다.
- `ventricle_related`: 뇌실 인접 구조로 전처리/분할 편차 영향을 받을 수 있어 주의가 필요합니다.
