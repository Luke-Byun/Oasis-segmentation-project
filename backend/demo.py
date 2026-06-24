# app/test_with_line.py
import json
from pathlib import Path
from typing import Dict, Any, Tuple

from rag.retriever import load_docs, TfidfRetriever
from rag.pipeline import generate_explanation
from rag.llm_client import OpenAIClient, OpenAIConfig

from dotenv import load_dotenv

load_dotenv() # .env에서 OPENAI_API_KEY 로드
DOCS_DIR = Path(__file__).resolve().parent / "docs"

LABEL_NAMES = {
    1:"L_Cerebral_WM", 2:"L_LatVent", 3:"L_InfLatVent", 4:"L_Cb_WM", 5:"L_Cb_Ctx",
    6:"L_Thalamus", 7:"L_Caudate", 8:"L_Putamen", 9:"L_Pallidum", 10:"V3", 11:"V4",
    12:"BrainStem", 13:"L_Hippocampus", 14:"L_Amygdala", 15:"CSF", 16:"L_Accumbens",
    17:"L_VentralDC", 18:"L_ChoroidPlexus", 19:"R_Cerebral_WM", 20:"R_LatVent",
    21:"R_InfLatVent", 22:"R_Cb_WM", 23:"R_Cb_Ctx", 24:"R_Thalamus", 25:"R_Caudate",
    26:"R_Putamen", 27:"R_Pallidum", 28:"R_Hippocampus", 29:"R_Amygdala"
}

LINE = """OAS1_0028\tAD\t611813\t0.19872902341074805\t0.035661223\t0.002687096\t0.020424541485715406\t0.095483424\t0.010365912460179826\t0.00580733\t0.007418934\t0.002866889\t0.00436081\t0.002670751\t0.032156884538249435\t0.005751757\t0.002075798\t0.002579219\t0.000836857\t0.006258448\t0.001153947\t0.432078102\t0.032588389\t0.002111756\t0.018871779448949272\t0.043170053594807564\t0.010285822628809784\t0.006327097\t0.006645822\t0.002682192\t0.005802427\t0.002147715"""

def parse_one_line_to_ratios(line: str) -> Tuple[str, str, Dict[str, Any]]:
    parts = line.strip().split()  # 탭/공백 자동 처리
    if len(parts) != 32:
        raise ValueError(f"컬럼 개수 이상: 기대 32개, 실제 {len(parts)}개")

    subject_id = parts[0]
    group = parts[1]             # 데이터셋 정답(배포 LLM 입력에는 넣지 않음)
    total_voxels = int(parts[2])

    ratio_vals = list(map(float, parts[3:]))  # 29개
    ratios = {"Total_Voxels": total_voxels}
    for label_id in range(1, 30):
        ratios[LABEL_NAMES[label_id]] = ratio_vals[label_id - 1]
    return subject_id, group, ratios

def ratios_to_llm_input(subject_id: str, ratios: Dict[str, Any], prediction: str, probability: float) -> Dict[str, Any]:
    roi_ratios = []
    ratio_sum = 0.0
    for label_id in range(1, 30):
        roi = LABEL_NAMES[label_id]
        val = float(ratios.get(roi, 0.0))
        ratio_sum += val
        roi_ratios.append({"label_id": label_id, "roi": roi, "ratio": val})

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
            "total_voxels": int(ratios["Total_Voxels"]),
            "ratio_sum": ratio_sum,
            "ratio_sum_error": abs(ratio_sum - 1.0),
        },
        "roi_ratios": roi_ratios,
        "model_output": {"prediction": prediction, "probability": float(probability)}
    }

def print_dashboard_report(report: dict, llm_input: dict):
    line = "=" * 80

    # ===============================
    # 1. Header (Prediction)
    # ===============================
    me = report.get("model_explanation", {})
    pred = me.get("prediction", "Unknown")
    prob = me.get("probability", None)

    print(line)
    print("🧠 Brain Volume Analysis Report")
    print(line)
    print(f"▶ Model Prediction : {pred}")
    if prob is not None:
        print(f"▶ Disease Probability : {prob:.2f}")
    print("⚠️  본 결과는 임상적 진단이 아닌 연구/보조 목적입니다.")
    print(line)

    # ===============================
    # 2. Summary
    # ===============================
    print("\n[ Summary ]")
    print("-" * 80)
    print(report.get("summary", "요약 정보 없음"))

    # ===============================
    # 3. Dashboard Explanation
    # ===============================
    dash = report.get("dashboard_explanation", {})
    if dash:
        print("\n[ Dashboard Overview ]")
        print("-" * 80)
        for x in dash.get("what_you_are_seeing", []):
            print(f"- {x}")

        print("\n  Where to start:")
        for x in dash.get("where_to_start", []):
            print(f"  • {x}")

    # ===============================
    # 4. Metric Explanation
    # ===============================
    metric = report.get("metric_explanation", {})
    if metric:
        print("\n[ Metric Explanation ]")
        print("-" * 80)
        print("Definitions:")
        for x in metric.get("definitions", []):
            print(f"- {x}")

        print("\nCommon misunderstandings:")
        for x in metric.get("common_misunderstandings", []):
            print(f"- {x}")

    # ===============================
    # 5. QC Explanation
    # ===============================
    qc_exp = report.get("qc_explanation", {})
    qc = llm_input.get("qc", {})

    print("\n[ Quality Check (QC) ]")
    print("-" * 80)
    print(f"- total_voxels      : {qc.get('total_voxels', 'N/A')}")
    print(f"- ratio_sum         : {qc.get('ratio_sum', 'N/A')}")
    print(f"- ratio_sum_error   : {qc.get('ratio_sum_error', 'N/A')}")

    if qc_exp:
        print("\nQC meaning:")
        for x in qc_exp.get("what_qc_means", []):
            print(f"- {x}")

        print("\nWhat to do if QC is abnormal:")
        for x in qc_exp.get("how_to_act", []):
            print(f"- {x}")

    # ===============================
    # 6. Key Findings (Interpretation 중심)
    # ===============================
    print("\n[ Key Findings (Interpretation) ]")
    print("-" * 80)

    kfs = report.get("key_findings", [])
    if not kfs:
        print("핵심 해석 항목이 없습니다.")
    else:
        for i, k in enumerate(kfs, 1):
            print(f"\n({i}) ROI : {k.get('roi', '')}")
            print(f"    ratio     : {k.get('ratio', 0.0):.6f}")
            print(f"    type      : {k.get('type_tag', 'unknown')}")
            print(f"    meaning   : {k.get('interpretation', '')}")

            cites = k.get("citations", [])
            if cites:
                print(f"    references: {', '.join(cites)}")

    # ===============================
    # 7. Model Explanation
    # ===============================
    print("\n[ Model Explanation ]")
    print("-" * 80)
    for x in me.get("what_it_means", []):
        print(f"- {x}")

    # ===============================
    # 8. How to Read Dashboard
    # ===============================
    print("\n[ How to Read This Dashboard ]")
    print("-" * 80)
    for x in report.get("how_to_read_dashboard", []):
        print(f"- {x}")

    # ===============================
    # 9. Warnings
    # ===============================
    print("\n[ Warnings ]")
    print("-" * 80)
    for x in report.get("warnings", []):
        print(f"⚠️  {x}")

    print("\n" + line)

def main():
    # 1) 입력 한 줄 파싱
    subject_id, true_group, ratios = parse_one_line_to_ratios(LINE)

    # 2) 여기서는 "테스트"니까 모델 출력을 임시로 넣는다.
    #    - 실제 배포에서는 분류 모델의 결과(pred, prob)를 넣으면 됨.
    #    - true_group는 LLM input에 넣지 않는다(데이터 누수 방지)
    prediction = "Disease"  # 테스트: AD/MCI는 Disease로 묶는 정책
    probability = 0.86      # 테스트용 임의 확률

    llm_input = ratios_to_llm_input(subject_id, ratios, prediction, probability)

    # 3) RAG 준비
    docs = load_docs(str(DOCS_DIR))
    retriever = TfidfRetriever.build(docs)

    # 4) OpenAI LLM 준비
    llm = OpenAIClient(OpenAIConfig(
        model="gpt-4o-mini",
        use_chat_completions=True,  # JSON 강제하려면 True 추천
        temperature=0.2,
        max_output_tokens=1200,
        force_json=True
    ))

    # 5) 생성
    report = generate_explanation(llm, retriever, llm_input, k=5)

    # 6) 출력
    # print("==== TRUE GROUP (debug only, NOT sent to LLM) ====")
    # print(true_group)
    # print("==== QC ====")
    # print(json.dumps(llm_input["qc"], ensure_ascii=False, indent=2))
    # print("==== REPORT(JSON) ====")
    # print(json.dumps(report, ensure_ascii=False, indent=2))
    print_dashboard_report(report, llm_input)

if __name__ == "__main__":
    main()
