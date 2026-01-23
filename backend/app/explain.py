# app/explain.py
from typing import Dict, Any, Tuple, List

from rag.retriever import load_docs, TfidfRetriever
from rag.pipeline import generate_explanation

LABEL_NAMES = {
    1:"L_Cerebral_WM", 2:"L_LatVent", 3:"L_InfLatVent", 4:"L_Cb_WM", 5:"L_Cb_Ctx",
    6:"L_Thalamus", 7:"L_Caudate", 8:"L_Putamen", 9:"L_Pallidum", 10:"V3", 11:"V4",
    12:"BrainStem", 13:"L_Hippocampus", 14:"L_Amygdala", 15:"CSF", 16:"L_Accumbens",
    17:"L_VentralDC", 18:"L_ChoroidPlexus", 19:"R_Cerebral_WM", 20:"R_LatVent",
    21:"R_InfLatVent", 22:"R_Cb_WM", 23:"R_Cb_Ctx", 24:"R_Thalamus", 25:"R_Caudate",
    26:"R_Putamen", 27:"R_Pallidum", 28:"R_Hippocampus", 29:"R_Amygdala"
}

# 입력에 type_tag를 넣어주면 LLM이 훨씬 안정적으로 "조직 vs 공간"을 구분한다.
FLUID_SPACE = {"CSF", "V3", "V4", "L_LatVent", "R_LatVent", "L_InfLatVent", "R_InfLatVent"}
VENTRICLE_RELATED = {"L_ChoroidPlexus"}  # 우측이 없어서 현재 라벨 기준으로 좌측만
def infer_type_tag(roi: str) -> str:
    if roi in FLUID_SPACE:
        return "fluid_space"
    if roi in VENTRICLE_RELATED:
        return "ventricle_related"
    return "tissue_like"

def ratios_to_llm_input(subject_id: str, ratios: Dict[str, Any], prediction: str, probability: float) -> Dict[str, Any]:
    roi_ratios: List[Dict[str, Any]] = []
    ratio_sum = 0.0

    for label_id in range(1, 30):
        roi = LABEL_NAMES[label_id]
        val = float(ratios.get(roi, 0.0))
        ratio_sum += val
        roi_ratios.append({
            "label_id": label_id,
            "roi": roi,
            "ratio": val,
            "type_tag": infer_type_tag(roi),
        })

    total_voxels = int(ratios.get("Total_Voxels", 0))

    return {
        "patient": {"id": subject_id},
        "volume_definition": {
            "method": "voxel_count_ratio",
            "numerator": "ROI voxel count (label_id)",
            "denominator": "All brain voxels where label > 0",
            "unit": "ratio",
            "note": "Voxel spacing(mm^3) is not applied"
        },
        "qc": {
            "total_voxels": total_voxels,
            "ratio_sum": ratio_sum,
            "ratio_sum_error": abs(ratio_sum - 1.0),
        },
        "roi_ratios": roi_ratios,
        "model_output": {"prediction": prediction, "probability": float(probability)}
    }

def pick_key_findings(input_json: Dict[str, Any], topk: int = 6) -> Dict[str, Any]:
    """
    MVP에서 key_findings는 '대표 ROI + 중요한 수치' 위주로 4~6개 고정.
    - 대표 ROI: 해마/편도체(기억/정서), 뇌실/CSF(공간), V3/V4, BrainStem
    - 부족하면 ratio 큰 순으로 채움 (단, fluid_space도 포함 가능하나 해석을 다르게 하도록 type_tag로 유도)
    """
    rois = input_json.get("roi_ratios", [])
    if not rois:
        input_json["ui_context"] = {"key_findings_rois": []}
        return input_json

    prefer = [
        "L_Hippocampus", "R_Hippocampus",
        "L_Amygdala", "R_Amygdala",
        "L_LatVent", "R_LatVent",
        "CSF", "V3", "V4",
        "BrainStem",
    ]

    # 1) prefer에서 존재하는 것 먼저
    selected = []
    seen = set()
    roi_map = {r["roi"]: r for r in rois}

    for name in prefer:
        if name in roi_map and name not in seen:
            selected.append(roi_map[name])
            seen.add(name)
        if len(selected) >= topk:
            break

    # 2) 부족하면 ratio 큰 순으로 채움
    if len(selected) < topk:
        sorted_by_ratio = sorted(rois, key=lambda x: x.get("ratio", 0.0), reverse=True)
        for r in sorted_by_ratio:
            if r["roi"] in seen:
                continue
            selected.append(r)
            seen.add(r["roi"])
            if len(selected) >= topk:
                break

    # 최소 4개는 보이게(데이터가 아주 빈약한 경우 대비)
    min_k = min(4, len(rois))
    selected = selected[:max(min_k, min(topk, len(selected)))]

    input_json["ui_context"] = {"key_findings_rois": [r["roi"] for r in selected]}
    return input_json

def explain_case(
    llm,
    docs_dir: str,
    subject_id: str,
    ratios: Dict[str, Any],
    model_output: Tuple[str, float]
) -> Dict[str, Any]:
    prediction, probability = model_output

    input_json = ratios_to_llm_input(subject_id, ratios, prediction, probability)
    input_json = pick_key_findings(input_json, topk=6)

    docs = load_docs(docs_dir)
    retriever = TfidfRetriever.build(docs)

    return generate_explanation(llm, retriever, input_json, k=6)