# Architecture and data flow

## Scope

This repository brings together three related research tracks:

1. segmentation model experiments;
2. ROI-level feature extraction and downstream classification; and
3. visualization and natural-language explanation prototypes.

They share concepts and artifacts but are not packaged as one production
service.

## End-to-end flow

```text
MRI (.nii.gz)
  -> preprocessing and nnU-Net inference
  -> segmentation mask with labels 1..29
  -> ROI voxel counts
  -> relative ROI ratios
      -> selected features -> Random Forest prediction
      -> local documentation retrieval -> LLM explanation
  -> Gradio visualization and research output
```

## Components

### Experiment notebooks

The files under `notebooks/oasis/` preserve model development and analysis
work. They are useful for tracing the research process, but some cells depend
on Colab paths, mounted Google Drive data, or packages not pinned at repository
level.

### Gradio application

`apps/gradio_app.py` accepts one NIfTI image, invokes `nnUNetv2_predict`, loads
the resulting mask, computes per-label counts, optionally runs a Random Forest
classifier, and renders selected ROI surfaces with Plotly.

The application expects the external nnU-Net environment to contain a dataset
and compatible trained checkpoint. It does not download a model.

### Explanation backend

The backend converts ROI ratios and model output into a structured input,
retrieves snippets from `backend/docs/` with TF-IDF, and requests a structured
explanation from an OpenAI model. The ground-truth group is deliberately not
included in the demo's LLM input.

### nnU-Net/MSD helper project

`nnUNet-segmentation-project/` is a related helper project originally built
around the Medical Segmentation Decathlon hippocampus dataset. Its absolute
volume utility uses voxel spacing, unlike the relative OASIS voxel-ratio
feature described below.

## Metric distinction

The OASIS downstream ratio is dimensionless:

```text
ROI ratio = count(label == ROI) / count(label > 0)
```

It should not be described as physical brain volume. Absolute volume requires
multiplying the voxel count by voxel spacing and reporting a unit such as
`mm³`.

## Artifact boundaries

The repository intentionally tracks source code and experiment records only.
Data, predictions, trained weights, classifier artifacts, API keys, and runtime
directories must remain external and are covered by `.gitignore`.
