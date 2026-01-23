# rag/build_docs.py
import os

LABEL_NAMES = {
    0:  "background",
    1:  "L_Cerebral_WM",
    2:  "L_LatVent",
    3:  "L_InfLatVent",
    4:  "L_Cb_WM",
    5:  "L_Cb_Ctx",
    6:  "L_Thalamus",
    7:  "L_Caudate",
    8:  "L_Putamen",
    9:  "L_Pallidum",
    10: "V3",
    11: "V4",
    12: "BrainStem",
    13: "L_Hippocampus",
    14: "L_Amygdala",
    15: "CSF",
    16: "L_Accumbens",
    17: "L_VentralDC",
    18: "L_ChoroidPlexus",
    19: "R_Cerebral_WM",
    20: "R_LatVent",
    21: "R_InfLatVent",
    22: "R_Cb_WM",
    23: "R_Cb_Ctx",
    24: "R_Thalamus",
    25: "R_Caudate",
    26: "R_Putamen",
    27: "R_Pallidum",
    28: "R_Hippocampus",
    29: "R_Amygdala",
}

ROI_DESC = {
    "Cerebral_WM": ("대뇌 백질", "대뇌의 신경섬유(연결)로 구성된 영역입니다. 전반적 구조/연결성과 관련된 지표로 해석될 수 있습니다.", "tissue_like"),
    "LatVent": ("측뇌실", "뇌실은 뇌척수액이 차는 공간입니다. 조직이 아니라 '공간'이므로 해석 방식이 다릅니다.", "fluid_space"),
    "InfLatVent": ("하측뇌실(측뇌실 하각)", "뇌척수액 공간(뇌실의 일부)입니다. 조직이 아니라 공간 지표입니다.", "fluid_space"),
    "Cb_WM": ("소뇌 백질", "소뇌 내부의 백질 영역입니다. 운동/균형 기능과 관련된 네트워크와 연관될 수 있습니다.", "tissue_like"),
    "Cb_Ctx": ("소뇌 피질", "소뇌의 회백질(피질) 영역입니다. 운동 조절 및 일부 인지 기능과 관련될 수 있습니다.", "tissue_like"),
    "Thalamus": ("시상", "감각/운동 정보 중계에 관여하는 심부핵입니다.", "tissue_like"),
    "Caudate": ("꼬리핵", "기저핵의 일부로 운동/학습/인지 기능과 관련될 수 있습니다.", "tissue_like"),
    "Putamen": ("조가비핵", "기저핵의 일부로 운동 기능과 관련될 수 있습니다.", "tissue_like"),
    "Pallidum": ("창백핵", "기저핵 회로의 일부로 운동 조절과 관련될 수 있습니다.", "tissue_like"),
    "Hippocampus": ("해마", "기억 형성과 관련된 구조로 알려져 있습니다. 단, 단일 지표만으로 임상적 결론을 내리면 안 됩니다.", "tissue_like"),
    "Amygdala": ("편도체", "정서 처리와 관련된 구조로 알려져 있습니다.", "tissue_like"),
    "Accumbens": ("측좌핵", "보상/동기 회로와 관련된 영역으로 알려져 있습니다.", "tissue_like"),
    "VentralDC": ("Ventral Diencephalon Complex", "간뇌 하부 영역(시상하부 주변 등)을 포함하는 구조 묶음입니다.", "tissue_like"),
    "ChoroidPlexus": ("맥락총", "뇌척수액 생성과 관련된 구조입니다. 뇌실과 인접해 전처리/분할 편차의 영향을 받을 수 있습니다.", "ventricle_related"),
    "V3": ("제3뇌실", "뇌척수액 공간(뇌실)입니다. 조직이 아닌 공간 지표입니다.", "fluid_space"),
    "V4": ("제4뇌실", "뇌척수액 공간(뇌실)입니다. 조직이 아닌 공간 지표입니다.", "fluid_space"),
    "BrainStem": ("뇌간", "생명 유지 및 신경 경로가 집중된 구조로 알려져 있습니다.", "tissue_like"),
    "CSF": ("뇌척수액(CSF)", "뇌척수액의 분할/추정 값입니다. 공간/액체 성격이 강해 조직과 다르게 해석해야 합니다.", "fluid_space"),
}

def parse_roi(name: str):
    if name in ["V3", "V4", "CSF", "BrainStem", "background"]:
        return None, name
    hemi = None
    core = name
    if name.startswith("L_"):
        hemi = "L"
        core = name[2:]
    elif name.startswith("R_"):
        hemi = "R"
        core = name[2:]
    return hemi, core

def build_roi_glossary_md(label_names: dict) -> str:
    lines = []
    lines.append("# ROI Glossary (Segmentation Labels)\n\n")
    lines.append("본 문서는 분할 라벨 기반 용적/용적률 대시보드 설명을 위한 ROI 사전입니다.\n\n")
    lines.append("⚠️ 주의: 아래 설명은 **일반적 의미**이며, 개별 환자에 대한 **진단/치료 결론을 의미하지 않습니다.**\n\n")
    lines.append("## Label List\n\n")
    lines.append("| label_id | roi_key | hemisphere | korean_name | type_tag | short_description |\n")
    lines.append("|---:|---|:---:|---|---|---|\n")

    for label_id in sorted(label_names.keys()):
        roi = label_names[label_id]
        if roi == "background":
            continue

        hemi, core = parse_roi(roi)
        base_key = core

        if base_key not in ROI_DESC:
            korean, desc, tag = (base_key, "구조 설명이 아직 등록되지 않았습니다. ROI 사전에 설명을 추가해 주세요.", "unknown")
        else:
            korean, desc, tag = ROI_DESC[base_key]

        hemi_str = "-" if hemi is None else hemi
        lines.append(f"| {label_id} | {roi} | {hemi_str} | {korean} | {tag} | {desc} |\n")

    lines.append("\n## Interpretation Notes\n")
    lines.append("- `tissue_like`: 조직(핵/백질/피질) 계열 ROI입니다.\n")
    lines.append("- `fluid_space`: 뇌실/CSF 등 공간/액체 계열 ROI로 조직과 동일하게 해석하지 않습니다.\n")
    lines.append("- `ventricle_related`: 뇌실 인접 구조로 전처리/분할 편차 영향을 받을 수 있어 주의가 필요합니다.\n")
    return "".join(lines)

def write_docs(out_dir: str):
    os.makedirs(out_dir, exist_ok=True)

    metric_definition = """# Metric Definition: Voxel-based Volume Ratio

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
"""

    model_card = """# Model Card (CN vs Disease)

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
"""

    dashboard_guide = """# Dashboard Guide (How to read this dashboard)

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
"""

    with open(os.path.join(out_dir, "metric_definition.md"), "w", encoding="utf-8") as f:
        f.write(metric_definition)
    with open(os.path.join(out_dir, "model_card.md"), "w", encoding="utf-8") as f:
        f.write(model_card)
    with open(os.path.join(out_dir, "roi_glossary.md"), "w", encoding="utf-8") as f:
        f.write(build_roi_glossary_md(LABEL_NAMES))
    with open(os.path.join(out_dir, "dashboard_guide.md"), "w", encoding="utf-8") as f:
        f.write(dashboard_guide)

if __name__ == "__main__":
    write_docs(os.path.join(os.path.dirname(__file__), "..", "docs"))
    print("Docs generated under ./docs (metric_definition, model_card, roi_glossary, dashboard_guide)")