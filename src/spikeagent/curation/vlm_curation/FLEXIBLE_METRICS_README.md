# Flexible Metrics System for VLM Curation

## Overview

The VLM curation system now supports flexible metrics selection, allowing users to choose which quality metrics to include in the assessment, just like they can choose which visual features to include.

## Key Changes

### 1. **Modified `run_vlm_curation()` function**
- Added `metrics_list` parameter to specify which metrics to use
- Maintains backward compatibility with existing code
- Validates that requested metrics exist in the data
- Provides warnings for missing metrics

### 2. **Dynamic Prompt Generation**
- Individual prompt files for each metric type in `prompts/metrics/`
- Prompts automatically adapt to include only selected metrics
- Each metric has specific guidelines and interpretation instructions

### 3. **Available Metric Prompts**
Currently supported metrics with individual prompt files:
- `snr` - Signal-to-Noise Ratio
- `isi_violations_ratio` - Contamination Rate (Hill et al. method, NOT a percentage)
- `l_ratio` - Cluster Separation Measure
- `nn_hit_rate` - Nearest Neighbor Hit Rate
- `nn_miss_rate` - Nearest Neighbor Miss Rate
- `amplitude_cutoff` - Amplitude-based Spike Loss Estimate
- `presence_ratio` - Temporal Consistency Measure

## Usage Examples

### Default Behavior (Backward Compatible)
```python
# Uses default metrics: ["snr", "isi_violations_ratio", "l_ratio"]
results_df = run_vlm_curation(
    model=model,
    sorting_analyzer=sorting_analyzer,
    img_df=img_df,
    with_metrics=True
)
```

### Custom Metrics Selection
```python
# Choose specific metrics
results_df = run_vlm_curation(
    model=model,
    sorting_analyzer=sorting_analyzer,
    img_df=img_df,
    with_metrics=True,
    metrics_list=["snr", "nn_hit_rate", "amplitude_cutoff"]
)
```

### Single Metric Assessment
```python
# Focus on just one metric
results_df = run_vlm_curation(
    model=model,
    sorting_analyzer=sorting_analyzer,
    img_df=img_df,
    with_metrics=True,
    metrics_list=["nn_hit_rate"]
)
```

## How the Prompt Adapts

### Before (Fixed Prompt)
```
You are given three numerical quality metrics for a spike-sorted unit:
- SNR: Signal-to-noise ratio  
- ISI Violations Ratio: Proportion of spikes violating the refractory period
- L-ratio: A measure of how well-separated the unit is...
```

### After (Dynamic Prompt)
When `metrics_list=["snr", "nn_hit_rate"]`:
```
You are given numerical quality metrics for a spike-sorted unit:

**SNR (Signal-to-Noise Ratio)**: A measure of signal strength relative to background noise.

Guidelines:
- SNR above ~4 generally indicates strong signal...

**NN Hit Rate**: The rate at which nearest neighbor classification correctly identifies the unit...

Guidelines:
- Values above ~0.5 (50%) generally indicate good unit distinctiveness...
```

## Adding New Metrics

To add support for a new metric:

1. Create a new prompt file: `prompts/metrics/your_metric_name.txt`
2. Include the metric description and interpretation guidelines
3. The system will automatically detect and use the new metric

Example metric prompt file:
```
**Your Metric Name**: Brief description of what it measures.

Guidelines:
- Threshold 1: Interpretation...
- Threshold 2: Interpretation...

In your reasoning, interpret what this metric suggests about...
```

## Benefits

1. **Flexibility**: Choose only relevant metrics for your analysis
2. **Adaptability**: Prompts automatically include appropriate guidance
3. **Extensibility**: Easy to add new metrics without code changes
4. **Backward Compatibility**: Existing code continues to work unchanged
5. **Robustness**: Graceful handling of missing or invalid metrics

## Implementation Details

- Metrics validation ensures only available metrics are used
- Warning messages for missing metrics
- Fallback to original prompt system if individual metric files don't exist
- Dynamic prompt generation based on selected metrics
- Maintains all existing async processing and error handling
