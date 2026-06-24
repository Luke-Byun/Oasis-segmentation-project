"""OASIS MRI segmentation and research visualization app."""

import os
import shutil
import subprocess
import tempfile
from pathlib import Path

import gradio as gr
import joblib
import nibabel as nib
import numpy as np
import plotly.graph_objects as go
from skimage import measure

# Runtime paths are configurable so the app works outside Google Colab.
RUNTIME_DIR = Path(
    os.getenv("OASIS_RUNTIME_DIR", str(Path(tempfile.gettempdir()) / "oasis-segmentation"))
)
os.environ.setdefault("nnUNet_raw", str(RUNTIME_DIR / "nnUNet_raw"))
os.environ.setdefault("nnUNet_preprocessed", str(RUNTIME_DIR / "nnUNet_preprocessed"))
os.environ.setdefault("nnUNet_results", str(RUNTIME_DIR / "nnUNet_results"))

DATASET_ID = os.getenv("OASIS_NNUNET_DATASET_ID", "1")
CONFIGURATION = os.getenv("OASIS_NNUNET_CONFIGURATION", "3d_fullres")
FOLD = os.getenv("OASIS_NNUNET_FOLD", "0")
CHECKPOINT = os.getenv("OASIS_NNUNET_CHECKPOINT", "checkpoint_best.pth")

# 2. 클래스 정의 (전체 29개)
CLASS_NAMES = [
    "L-Cerebral-WM", "L-Lat-Vent", "L-Inf-Lat-Vent", "L-Cereb-WM", "L-Cereb-Cortex", 
    "L-Thalamus", "L-Caudate", "L-Putamen", "L-Pallidum", "3rd-Vent", 
    "4th-Vent", "Brain-Stem", "L-Hippocampus", "L-Amygdala", "CSF", 
    "L-Accumbens", "L-VentralDC", "L-choroid-plexus", "R-Cerebral-WM", 
    "R-Lat-Vent", "R-Inf-Lat-Vent", "R-Cereb-WM", "R-Cereb-Cortex", 
    "R-Thalamus", "R-Caudate", "R-Putamen", "R-Pallidum", "R-Hippocampus", "R-Amygdala"
]

# 3. 모델용 10개 피처 매핑 (순서 중요)
# CLASS_NAMES 내의 실제 이름과 매칭되도록 수정
RF_FEATURES = [
    "L-Hippocampus", "L-Amygdala", "L-Lat-Vent", 
    "L-Inf-Lat-Vent", "L-Cereb-Cortex",
    "R-Hippocampus", "R-Amygdala", "R-Lat-Vent", 
    "R-Inf-Lat-Vent", "R-Cereb-Cortex"
]

# 모델 로드
MODEL_PATH = Path(os.getenv("OASIS_RF_MODEL", "artifacts/oasis_rf_model.joblib"))
rf_model = joblib.load(MODEL_PATH) if MODEL_PATH.exists() else None

# 데이터 캐시
cache = {"orig": None, "pred": None, "total_v": 0, "counts": {}, "diagnosis": ""}

def get_mesh(data, label_idx, color, name):
    binary_mask = (data == label_idx).astype(float)
    if np.sum(binary_mask) < 10: return None
    verts, faces, _, _ = measure.marching_cubes(binary_mask, level=0.5, step_size=2)
    return go.Mesh3d(x=verts[:, 0], y=verts[:, 1], z=verts[:, 2], i=faces[:, 0], j=faces[:, 1], k=faces[:, 2],
                     color=color, opacity=0.7, name=name)

def run_analysis(mri_file):
    if mri_file is None:
        return "파일을 업로드하세요.", go.Figure(), "데이터 없음", "진단 대기 중"
    
    in_dir, out_dir = RUNTIME_DIR / "input", RUNTIME_DIR / "output"
    for directory in (in_dir, out_dir):
        if directory.exists():
            shutil.rmtree(directory)
        directory.mkdir(parents=True, exist_ok=True)

    input_path = in_dir / "sample_0000.nii.gz"
    source_path = Path(getattr(mri_file, "name", mri_file))
    shutil.copy2(source_path, input_path)

    # nnU-Net 예측 실행
    cmd = [
        "nnUNetv2_predict",
        "-i", str(in_dir),
        "-o", str(out_dir),
        "-d", DATASET_ID,
        "-c", CONFIGURATION,
        "-f", FOLD,
        "-chk", CHECKPOINT,
        "--disable_progress_bar",
    ]
    try:
        subprocess.run(cmd, check=True)
    except (OSError, subprocess.CalledProcessError) as exc:
        return f"분석 에러: {exc}", go.Figure(), "에러", "에러"

    # 결과 로드
    res_path = out_dir / "sample.nii.gz"
    cache["orig"] = nib.load(input_path).get_fdata()
    pred_data = nib.load(res_path).get_fdata()
    cache["pred"] = pred_data
    
    # 29개 전체 복셀 합 계산 (분모)
    total_v_sum = np.sum(pred_data > 0)
    cache["total_v"] = total_v_sum
    
    # 모든 클래스 카운트 저장
    for i, name in enumerate(CLASS_NAMES):
        cache["counts"][name] = np.sum(pred_data == (i + 1))

    # --- 머신러닝 진단 (10개 피처 추출) ---
    diagnosis_result = "모델 로드 실패"
    if rf_model:
        feature_values = []
        for feat_name in RF_FEATURES:
            count = cache["counts"].get(feat_name, 0)
            ratio = count / total_v_sum if total_v_sum > 0 else 0
            feature_values.append(ratio)
        
        # 1 x 10 형태로 변환 후 예측
        input_data = np.array(feature_values).reshape(1, -1)
        prediction = rf_model.predict(input_data)[0]
        diagnosis_result = "⚠️ 질환 의심 (MCI/AD)" if prediction == 1 else "✅ 정상 (Normal)"
    
    cache["diagnosis"] = diagnosis_result
    fig, _ = update_viz([])
    
    return "분석 및 진단 완료!", fig, f"전체 뇌 용적: {int(total_v_sum):,} voxels", diagnosis_result

def update_viz(selected_names):
    if cache["pred"] is None:
        return go.Figure(), "분석을 먼저 실행해주세요."
    
    fig = go.Figure()
    import plotly.express as px
    colors = px.colors.qualitative.Alphabet + px.colors.qualitative.Dark24

    # 뇌 윤곽 (Outline)
    v, f, _, _ = measure.marching_cubes((cache["orig"] > np.mean(cache["orig"])).astype(float), level=0.5, step_size=3)
    fig.add_trace(go.Mesh3d(x=v[:, 0], y=v[:, 1], z=v[:, 2], i=f[:, 0], j=f[:, 1], k=f[:, 2], 
                           color='lightgray', opacity=0.03, name='Outline'))

    report = f"## 🩺 AI 진단 결과: {cache['diagnosis']}\n---\n### 📊 선택 구조 용적률\n"
    for name in selected_names:
        idx = CLASS_NAMES.index(name) + 1
        mesh = get_mesh(cache["pred"], idx, colors[idx % len(colors)], name)
        if mesh:
            fig.add_trace(mesh)
            ratio = (cache["counts"][name] / cache["total_v"]) * 100
            report += f"- **{name}**: `{ratio:.4f}%` ({int(cache['counts'][name]):,} vox)\n"

    # 두 번째 사진 스타일 레이아웃 (축과 격자 표시)
    fig.update_layout(
        scene=dict(
            aspectmode='data',
            xaxis=dict(title='X Axis', showgrid=True),
            yaxis=dict(title='Y Axis', showgrid=True),
            zaxis=dict(title='Z Axis', showgrid=True)
        ),
        height=600, showlegend=False, margin=dict(l=0, r=0, b=0, t=0)
    )
    return fig, report

# --- Gradio UI ---
try:
    gr.close_all()
except AttributeError:
    pass

with gr.Blocks(theme=gr.themes.Soft()) as demo:
    gr.Markdown("# 🧠 Brain AI Segmentation & Diagnosis System")
    
    with gr.Row():
        with gr.Column(scale=1):
            mri_input = gr.File(label="1. MRI 업로드 (.nii.gz)")
            btn_run = gr.Button("2. 분석 및 진단 실행", variant="primary")
            status_txt = gr.Textbox(label="상태", interactive=False)
            diag_output = gr.Textbox(label="3. AI 진단 결과", interactive=False)
            
            gr.Markdown("### 4. 구조 시각화 (체크 시 3D 표시)")
            class_select = gr.CheckboxGroup(choices=CLASS_NAMES, label=None)
            
        with gr.Column(scale=2):
            vol_result_display = gr.Markdown("### 📊 분석 통계")
            plot_view = gr.Plot(label="3D 시각화")

    btn_run.click(fn=run_analysis, inputs=mri_input, outputs=[status_txt, plot_view, vol_result_display, diag_output])
    class_select.change(fn=update_viz, inputs=class_select, outputs=[plot_view, vol_result_display])

def main():
    """Launch the local Gradio interface."""
    share = os.getenv("GRADIO_SHARE", "false").lower() in {"1", "true", "yes"}
    demo.queue().launch(share=share)


if __name__ == "__main__":
    main()
