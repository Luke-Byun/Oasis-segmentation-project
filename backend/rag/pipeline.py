# rag/pipeline.py
import json
from typing import Dict, Any, List

from rag.retriever import TfidfRetriever
from rag.prompts import SYSTEM_PROMPT, USER_PROMPT_TEMPLATE

def build_rag_blocks(hits: List[Dict[str, Any]]) -> str:
    blocks = []
    for h in hits:
        blocks.append(f"- doc_id: {h['doc_id']}\n  snippet: {h['snippet']}\n")
    return "\n".join(blocks)

def safe_json_load(s: str) -> Dict[str, Any]:
    # LLM이 실수로 앞뒤 텍스트를 붙이는 경우 대비(최소 방어)
    s = s.strip()
    first = s.find("{")
    last = s.rfind("}")
    if first == -1 or last == -1 or last <= first:
        raise ValueError("No JSON object found in LLM output")
    return json.loads(s[first:last+1])

def generate_explanation(llm, retriever: TfidfRetriever, input_json: Dict[str, Any], k: int = 5) -> Dict[str, Any]:
    # 검색 query를 "지표 정의 + ROI + 예측" 중심으로 구성
    rois = [r["roi"] for r in input_json.get("roi_ratios", [])[:20]]
    pred = input_json.get("model_output", {}).get("prediction", "")
    query = f"voxel ratio metric interpretation {pred} ROI " + " ".join(rois)

    hits = retriever.search(query, k=k)
    rag_blocks = build_rag_blocks(hits)

    user_prompt = USER_PROMPT_TEMPLATE.format(
        input_json=json.dumps(input_json, ensure_ascii=False),
        rag_blocks=rag_blocks
    )

    raw = llm.generate(SYSTEM_PROMPT, user_prompt)
    out = safe_json_load(raw)

    # 최소 필드 보정
    out.setdefault("warnings", [])
    out.setdefault("how_to_read_dashboard", [])
    return out