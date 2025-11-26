# API Reference

This document provides detailed documentation for SpikeAgent's programmatic API.

## Overview

SpikeAgent provides both a web interface and a Python API. This reference covers the Python API for programmatic usage.

## Installation

To use SpikeAgent programmatically, install from source:

```bash
pip install -e .
```

## Core Modules

### `spikeagent.app`

Main application module containing the Streamlit interface and core functionality.

#### `spikeagent.app.tool.si_custom`

Custom plotting and image generation functions for SpikeInterface.

##### `create_unit_img_df(sortinganalyzer, unit_ids=None, features=UNIT_FEATURES, load_if_exists=True, save_folder=None)`

Creates a DataFrame of base64-encoded images for specified units and features.

**Parameters:**
- `sortinganalyzer` (SortingAnalyzer): The analyzer object containing the data
- `unit_ids` (list, optional): List of unit IDs to generate images for. If None, all units are used
- `features` (list, optional): List of feature plots to generate
- `load_if_exists` (bool, optional): If True, loads cached CSV if available
- `save_folder` (str or Path, optional): Folder to save the image DataFrame

**Returns:**
- `pd.DataFrame`: DataFrame with unit_id as index and features as columns, containing base64-encoded PNG images

##### `create_merge_img_df(sortinganalyzer, unit_groups, features=MERGE_FEATURES, load_if_exists=True, save_folder=None)`

Creates a DataFrame of base64-encoded images for merge groups.

**Parameters:**
- `sortinganalyzer` (SortingAnalyzer): The analyzer object
- `unit_groups` (list): List of unit groups to analyze for merging
- `features` (list, optional): List of feature plots to generate
- `load_if_exists` (bool, optional): If True, loads cached CSV if available
- `save_folder` (str or Path, optional): Folder to save the image DataFrame

**Returns:**
- `pd.DataFrame`: DataFrame with group indices and base64-encoded images

### `spikeagent.curation`

Curation and VLM analysis modules.

#### `spikeagent.curation.vlm_curation`

Vision-Language Model based curation functions.

##### `run_vlm_curation(model, sorting_analyzer, img_df, features=MODALITY, good_ids=[], bad_ids=[], with_metrics=False, metrics_list=None, unit_ids=None, num_workers=50)`

Runs VLM curation to classify units as "Good" or "Bad".

**Parameters:**
- `model`: The VLM model instance (from `get_model()`)
- `sorting_analyzer` (SortingAnalyzer): The analyzer with computed extensions
- `img_df` (pd.DataFrame): DataFrame from `create_unit_img_df()`
- `features` (list): List of features to analyze
- `good_ids` (list): Pre-labeled good unit IDs for few-shot learning
- `bad_ids` (list): Pre-labeled bad unit IDs for few-shot learning
- `with_metrics` (bool): Whether to include quality metrics in analysis
- `metrics_list` (list, optional): Specific metrics to include
- `unit_ids` (list, optional): Subset of units to analyze
- `num_workers` (int): Number of parallel workers for async processing

**Returns:**
- `pd.DataFrame`: Results with classifications, scores, and reasoning

##### `plot_spike_images_with_result(results_df, encoded_img_df, feature="waveform_single")`

Plots units with their VLM classification results.

**Parameters:**
- `results_df` (pd.DataFrame): Results from `run_vlm_curation()`
- `encoded_img_df` (pd.DataFrame): Image DataFrame from `create_unit_img_df()`
- `feature` (str): Feature to display in plots

#### `spikeagent.curation.vlm_merge`

Vision-Language Model based merge analysis functions.

##### `run_vlm_merge(model, merge_unit_groups, img_df, features=MODALITY, good_merge_groups=[], bad_merge_groups=[], num_workers=50)`

Runs VLM merge analysis to determine if units should be merged.

**Parameters:**
- `model`: The VLM model instance
- `merge_unit_groups` (list): List of unit groups to analyze
- `img_df` (pd.DataFrame): DataFrame from `create_merge_img_df()`
- `features` (list): List of features to analyze
- `good_merge_groups` (list): Pre-labeled good merge groups for few-shot learning
- `bad_merge_groups` (list): Pre-labeled bad merge groups for few-shot learning
- `num_workers` (int): Number of parallel workers

**Returns:**
- `pd.DataFrame`: Results with merge decisions and reasoning

##### `plot_merge_results(results_df, encoded_img_df)`

Plots merge groups with their classification results.

**Parameters:**
- `results_df` (pd.DataFrame): Results from `run_vlm_merge()`
- `encoded_img_df` (pd.DataFrame): Image DataFrame from `create_merge_img_df()`

### `spikeagent.app.tool.utils`

Utility functions.

##### `get_model(model_name, temperature=0)`

Gets a VLM model instance.

**Parameters:**
- `model_name` (str): Model name ("gpt-4o", "claude_3_7_sonnet", "gemini-pro-vision")
- `temperature` (float): Model temperature parameter

**Returns:**
- Model instance for use with VLM functions

## Example Usage

```python
import spikeinterface as si
from spikeagent.app.tool.si_custom import create_unit_img_df
from spikeagent.curation.vlm_curation import run_vlm_curation, plot_spike_images_with_result
from spikeagent.app.tool.utils import get_model

# Create or load a SortingAnalyzer
sorting_analyzer = si.create_sorting_analyzer(...)

# Compute required extensions
sorting_analyzer.compute("waveforms")
sorting_analyzer.compute("templates")
# ... other extensions

# Create image DataFrame
features = ["waveform_single", "autocorr", "spike_locations"]
img_df = create_unit_img_df(sorting_analyzer, features=features)

# Run VLM curation
model = get_model("gpt-4o")
results_df = run_vlm_curation(
    model=model,
    sorting_analyzer=sorting_analyzer,
    img_df=img_df,
    features=features,
    with_metrics=True
)

# Visualize results
plot_spike_images_with_result(results_df, img_df, feature="waveform_single")

# Apply curation
good_units = results_df[results_df['final_classification'] == 'Good'].index.tolist()
curated_analyzer = sorting_analyzer.select_units(good_units)
```

## Feature Lists

### Unit Features
- `waveform_single`: Single-channel waveform plot
- `waveform_multi`: Multi-channel template plot
- `autocorr`: Autocorrelogram
- `spike_locations`: Spatial spike locations
- `amplitude_plot`: Amplitude distribution over time

### Merge Features
- `waveform_single`: Single-channel waveform comparison
- `waveform_multi`: Multi-channel template comparison
- `crosscorrelograms`: Cross-correlogram between units
- `spike_locations`: Spatial location comparison
- `amplitude_plot`: Amplitude distribution comparison
- `pca_clustering`: PCA space clustering analysis

## See Also

- [Jupyter Notebook Tutorials](../notebook%20tutorials/) for complete examples
- [User Guide](user-guide.md) for workflow guidance
- [SpikeInterface Documentation](https://spikeinterface.readthedocs.io/) for underlying framework

