# OASIS Brain Segmentation Project

OASIS 뇌 MRI를 대상으로 뇌 구조를 segmentation하고, 분할 결과에서 얻은 ROI별 상대 용적 비율을 이용해 인지 저하 관련 분류와 결과 해석 흐름을 실험한 프로젝트입니다.

이 저장소는 크게 세 부분으로 구성됩니다.

1. `U-Net`, `DeepLab`, `Light3DHS`, `nnU-Net` 기반 segmentation 실험 노트북
2. nnU-Net 예측 마스크에서 29개 뇌 구조의 voxel ratio를 계산해 `CN`과 `Disease(AD + MCI)`를 구분하는 분석 흐름
3. segmentation 결과를 3D로 확인하는 Gradio UI와 ROI 지표를 설명하는 RAG 기반 backend prototype

> 이 프로젝트의 분류 결과와 설명 문구는 연구 및 보조 목적입니다. 임상 진단이나 치료 결정을 대체하지 않습니다.

## Project Flow

```text
OASIS MRI
   |
   v
Segmentation model experiments
U-Net / DeepLab / Light3DHS / nnU-Net
   |
   v
29 ROI segmentation mask
   |
   +--> 3D ROI visualization with Gradio
   |
   v
ROI voxel ratio extraction
   |
   +--> CN vs Disease classification
   |
   v
RAG explanation for dashboard metrics and ROI context
```

## Main Scope

### Segmentation

- OASIS subcortical brain structures are represented with 29 ROI labels.
- The notebooks compare or prototype several medical image segmentation approaches.
- The nnU-Net workflow remaps label ids to a continuous `1` to `29` label space before training.

### Volumetric Features

The primary downstream feature is a voxel-count ratio.

```text
ROI ratio = ROI voxel count / all non-background brain voxels
```

- `Total_Voxels` is computed from voxels where the segmentation label is greater than `0`.
- The backend explanation module treats this value as a relative ratio, not an absolute `mm^3` volume.
- Tissue-like ROIs and fluid-space ROIs such as ventricles or CSF should not be interpreted in the same way.

### Classification and Explanation

- The analysis flow groups `AD` and `MCI` into `Disease` for a `CN` vs `Disease` binary task.
- The Gradio prototype uses selected ROI ratios as Random Forest inputs after nnU-Net prediction.
- The backend prototype retrieves local markdown documentation and asks an LLM to explain model output, metric definitions, QC signals, and representative ROI findings.

## Repository Structure

```text
.
|-- project2_U_Net.ipynb              # U-Net experiment notebook
|-- project2_DeepLab.ipynb            # DeepLab experiment notebook
|-- project2_Light3DHS.ipynb          # Light3DHS experiment notebook
|-- project2_nnU_Net.ipynb            # nnU-Net-style experiment notebook
|-- Segmentation_Returns.ipynb        # OASIS sampling, inference, ROI analysis workflow
|-- ml_analysis.ipynb                 # Downstream machine learning analysis
|-- nnUnet_train.py                   # Colab-oriented nnU-Net training cells
|-- gradio.py                         # nnU-Net inference, diagnosis, 3D ROI visualization UI
|-- backend/
|   |-- app/explain.py                # ROI ratio -> explanation input adapter
|   |-- rag/                          # Retriever, prompts, LLM client, explanation pipeline
|   |-- docs/                         # Model card, metric guide, ROI glossary, dashboard guide
|   |-- test.py                       # RAG explanation smoke script
|   `-- requirements.txt
`-- nnUNet-segmentation-project/      # nnU-Net/MSD helper scripts and volume calculator
```

`nnUNet-segmentation-project/` contains helper scripts that were written around an MSD Hippocampus nnU-Net workflow. The OASIS training path used by this repository is mainly documented in the root notebooks and `nnUnet_train.py`.

## Data and Artifacts

Large research assets are not stored in this repository. To reproduce the full pipeline you need the corresponding local or Colab assets.

- OASIS MRI files and segmentation labels in NIfTI format
- nnU-Net raw, preprocessed, and result directories
- Trained nnU-Net checkpoints for inference
- The Random Forest artifact expected by the Gradio prototype, such as `oasis_rf_model.joblib`
- An OpenAI API key only when running the LLM/RAG explanation prototype

Several experiment files use Google Colab paths such as `/content/...` and Google Drive paths. Update those paths for your runtime before training or inference.

## Setup

Create a Python environment first.

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
```

For nnU-Net and medical imaging helpers:

```bash
pip install -r nnUNet-segmentation-project/requirements.txt
```

For the RAG explanation backend:

```bash
pip install -r backend/requirements.txt
pip install openai scikit-learn
```

The notebooks may require additional packages depending on the selected experiment cell and Colab runtime.

## nnU-Net Workflow

The root OASIS training notes are in `nnUnet_train.py` and the notebooks. They show the main steps below.

1. Set nnU-Net environment directories.

```bash
export nnUNet_raw=/path/to/nnUNet_raw
export nnUNet_preprocessed=/path/to/nnUNet_preprocessed
export nnUNet_results=/path/to/nnUNet_results
```

2. Prepare an OASIS nnU-Net dataset folder such as `Dataset001_BrainSeg` or `Dataset001_OASIS_Subcort`.
3. Remap segmentation labels into the continuous label ids used by the OASIS workflow.
4. Plan, preprocess, train, and run inference.

```bash
nnUNetv2_plan_and_preprocess -d 1 --verify_dataset_integrity
nnUNetv2_train 1 3d_fullres 0
nnUNetv2_predict -i /path/to/imagesTs -o /path/to/predictions -d 1 -c 3d_fullres -f 0
```

nnU-Net input image names must follow its channel naming rule, for example `sample_0000.nii.gz`.

## Gradio Prototype

`gradio.py` provides a research UI that:

- accepts a `.nii.gz` MRI file
- runs `nnUNetv2_predict`
- renders selected ROI surfaces in 3D with Plotly
- displays total segmented voxel count and a classification result when the Random Forest artifact is available

Before launching it, update the Colab-specific constants in `gradio.py`.

- `nnUNet_raw`, `nnUNet_preprocessed`, `nnUNet_results`
- `MODEL_PATH`
- temporary input/output directories
- nnU-Net dataset id, fold, configuration, and checkpoint name in the prediction command

Then install its runtime dependencies and run:

```bash
pip install gradio plotly scikit-image joblib nibabel numpy
python gradio.py
```

## RAG Explanation Prototype

The backend prototype uses local documents in `backend/docs/` as retrieval context. It explains dashboard metrics and model output without sending the ground-truth class label to the LLM input in the included test flow.

```bash
cd backend
export OPENAI_API_KEY=your_api_key
python test.py
```

Relevant docs:

- `backend/docs/model_card.md`
- `backend/docs/metric_definition.md`
- `backend/docs/roi_glossary.md`
- `backend/docs/dashboard_guide.md`

## Experiment Files

| File | Purpose |
| --- | --- |
| `project2_U_Net.ipynb` | U-Net segmentation experiments |
| `project2_DeepLab.ipynb` | DeepLab segmentation experiments |
| `project2_Light3DHS.ipynb` | Light3DHS segmentation experiments |
| `project2_nnU_Net.ipynb` | nnU-Net-style 3D experiment and evaluation cells |
| `Segmentation_Returns.ipynb` | OASIS data sampling, nnU-Net inference, ROI result extraction |
| `ml_analysis.ipynb` | ROI-derived machine learning analysis |
| `U_Net_for_Decathlon_dataset.ipynb` | Hippocampus/Decathlon U-Net reference experiment |

## Notes and Limitations

- The repository currently contains research notebooks and prototypes rather than a single packaged training CLI.
- Runtime paths in `nnUnet_train.py` and `gradio.py` are Colab-oriented.
- Trained checkpoints, OASIS data, and the Random Forest model artifact are required for end-to-end inference but are not included here.
- ROI ratios are sensitive to segmentation quality, preprocessing differences, and dataset distribution shift.
- The `Disease` class merges `AD` and `MCI`; it is not an AD/MCI differential diagnosis model.
