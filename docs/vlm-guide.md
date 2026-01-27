# VLM Curation and Merging Guide

This guide provides an in-depth explanation of how Vision-Language Models (VLMs) are used in SpikeAgent for automated unit curation and merging, including how to customize prompts and behavior.

## Table of Contents

- [Architecture Overview](#architecture-overview)
- [VLM Curation](#vlm-curation)
- [VLM Merge Analysis](#vlm-merge-analysis)
- [Prompt System](#prompt-system)
- [Customizing Prompts](#customizing-prompts)
- [Best Practices](#best-practices)
- [Advanced Topics](#advanced-topics)

---

## Architecture Overview

SpikeAgent uses an **Ensemble of Experts** approach where:
1. **Feature Experts**: Specialized AI reviewers analyze individual modalities (waveforms, locations, etc.)
2. **Head Reviewer**: Aggregates expert reports and makes final classification decisions
3. **Consensus Voting**: Multiple independent reviews can be combined for robust decisions

### Key Components

- **Image Encoding**: Neural data features are rendered as diagnostic plots and encoded as base64 images
- **Asynchronous Processing**: Multiple units are processed in parallel using `asyncio` for efficiency
- **Few-Shot Learning**: Optional example units can guide the AI's decision-making
- **Quality Metrics Integration**: Quantitative metrics can augment visual analysis

---

## VLM Curation

### How It Works

Unit curation classifies each sorted unit as **"Good"** (well-isolated neuron) or **"Bad"** (noise/artifact).

#### Workflow:

1. **Image Generation**: For each unit, diagnostic images are generated:
   - `waveform_single`: Average waveform on peak channel
   - `waveform_multi`: Multi-channel template view
   - `autocorr`: Autocorrelogram (ISI distribution)
   - `spike_locations`: Spatial scatter plot
   - `amplitude_plot`: Amplitude over time

2. **Expert Analysis**: Each modality is sent to a specialized prompt:
   ```
   User → Image → [Waveform Expert] → Analysis
                → [Autocorr Expert] → Analysis
                → [Location Expert] → Analysis
                ...
   ```

3. **Head Aggregation**: All expert analyses are combined:
   ```
   [Head Reviewer] receives:
   - Waveform Expert Report
   - Autocorr Expert Report
   - Location Expert Report
   (+ optional quality metrics)
   
   → Final Decision: Good/Bad + Quality Score (0.0-1.0)
   ```

4. **Consensus (Optional)**: Multiple independent reviewers repeat steps 2-3, and results are combined by majority vote.

### Parameters

- `num_reviewers` (default=1): Number of independent reviews per unit. Use `1` (default) for speed, `3` for robustness.
- `with_metrics` (default=False): Include quantitative quality metrics in the prompt.
- `metrics_list`: Specific metrics to include (e.g., `["snr", "isi_violations_ratio"]`).
- `good_ids` / `bad_ids`: Example unit IDs for few-shot learning.

---

## VLM Merge Analysis

### How It Works

Merge analysis determines if two or more units should be merged because they likely represent the same neuron.

#### Workflow:

1. **Candidate Identification**: Use SpikeInterface's `compute_merge_unit_groups()` to find similar units based on template similarity.

2. **Comparison Images**: For each candidate group, generate overlaid comparison plots:
   - `waveform_single`: Overlaid waveforms (color-coded by unit)
   - `crosscorrelograms`: Cross-correlation between units
   - `amplitude_plot`: Amplitude distributions with histograms

3. **Expert Analysis**: Each comparison modality is analyzed by a specialized prompt.

4. **Head Decision**: The head reviewer determines:
   - **"merge"**: Units should be combined
   - **"not merge"**: Units are distinct neurons

### Decision Criteria

The AI looks for:
- **Waveform similarity**: Near-identical shapes suggest same neuron
- **Temporal relationship**: Cross-correlograms show if units fire independently
- **Amplitude separation**: Clear separation suggests distinct neurons
- **Spatial proximity**: Similar locations support merging

---

## Prompt System

### Directory Structure

Prompts are organized as plain text files:

```
src/spikeagent/curation/
├── vlm_curation/prompts/
│   ├── head.txt                    # Head reviewer prompt
│   ├── modality/                   # Feature expert prompts
│   │   ├── waveform_single.txt
│   │   ├── waveform_multi.txt
│   │   ├── autocorr.txt
│   │   ├── spike_locations.txt
│   │   └── amplitude_plot.txt
│   ├── metrics_header.txt          # Quality metrics header
│   ├── metrics/                    # Individual metric descriptions
│   │   ├── snr.txt
│   │   ├── isi_violations_ratio.txt
│   │   ├── presence_ratio.txt
│   │   └── ...
│   └── fewshot_instruction.txt     # Few-shot learning instructions
│
└── vlm_merge/prompts/
    ├── head.txt                    # Merge head reviewer prompt
    ├── modality/                   # Merge feature expert prompts
    │   ├── waveform_single.txt
    │   ├── crosscorrelograms.txt
    │   ├── amplitude_plot.txt
    │   └── ...
    └── fewshot_instruction.txt
```

### Prompt Loading

Prompts are loaded dynamically by `prompt_loader.py`:

```python
# Curation prompts
from spikeagent.curation.vlm_curation.prompt_loader import load_all_prompts

prompts = load_all_prompts()
# Access: prompts["modality"]["waveform_single"]

# Merge prompts
from spikeagent.curation.vlm_merge.prompt_loader import load_all_prompts
```

---

## Customizing Prompts

### Step 1: Locate the Prompt File

Navigate to the appropriate directory:
- **Curation modality prompts**: `src/spikeagent/curation/vlm_curation/prompts/modality/`
- **Curation head prompt**: `src/spikeagent/curation/vlm_curation/prompts/head.txt`
- **Merge modality prompts**: `src/spikeagent/curation/vlm_merge/prompts/modality/`
- **Merge head prompt**: `src/spikeagent/curation/vlm_merge/prompts/head.txt`

### Step 2: Edit the Prompt

Open the relevant `.txt` file in a text editor. For example, to modify the waveform expert for curation:

```bash
nano src/spikeagent/curation/vlm_curation/prompts/modality/waveform_single.txt
```

### Step 3: Understand the Prompt Structure

Each modality prompt typically contains:
1. **Role definition**: What the expert should focus on
2. **Visual cues**: What patterns indicate good/bad units
3. **Decision criteria**: Specific guidelines for classification

Example structure (waveform expert):
```
You are an expert in analyzing neural spike waveforms.

Your task is to assess the quality of this unit based on its average waveform plot.

Good units typically show:
- Clean, stereotyped waveform shape
- Low noise/jitter
- Consistent amplitude

Bad units typically show:
- Noisy or irregular waveforms
- Artifacts or drift
- Very low amplitude

Provide your analysis focusing on waveform quality.
```

### Step 4: Test Your Changes

After modifying a prompt:
1. Restart the SpikeAgent application (if running)
2. Run a small test dataset
3. Review AI decisions to ensure prompts are effective

### Tips for Effective Prompts

- **Be specific**: Clearly define what to look for
- **Use examples**: Describe concrete patterns (e.g., "sharp peak followed by trough")
- **Set scope**: Tell the expert to focus ONLY on their modality
- **Avoid jargon**: Use clear, descriptive language
- **Test iteratively**: Refine prompts based on AI performance

---

## Best Practices

### 1. Choosing the Right Model

- **For speed** (default): Use `gpt-4o` with `num_reviewers=1` for curation
- **For robust consensus**: Use `gpt-4.1` or `gpt-4o` with `num_reviewers=3`
- **For merge analysis**: Both `gpt-4.1` and `gpt-4o` are highly effective

### 2. Feature Selection

**Curation essentials:**
- `waveform_single` + `autocorr` + `spike_locations` → Good baseline
- Add `amplitude_plot` for drift detection
- Add `waveform_multi` for probe geometry context

**Merge essentials:**
- `waveform_single` + `crosscorrelograms` → Minimum viable set
- Add `amplitude_plot` for temporal context

### 3. Quality Metrics Integration

Enable metrics for:
- **High-noise datasets**: Quantitative SNR helps AI decisions
- **Strict curation**: ISI violations provide objective contamination measure
- **Validation**: Compare AI decisions against traditional thresholds

Recommended metrics:
```python
metrics_list = ["snr", "isi_violations_ratio", "presence_ratio"]
```

### 4. Few-Shot Learning

Provide examples when:
- Working with unusual neuron types (e.g., very fast-spiking)
- Dataset has specific artifacts
- You want AI to match your personal curation style

How to use:
```python
# Manually label a few units
good_ids = [5, 12, 23]
bad_ids = [3, 8, 19]

results = run_vlm_curation(
    model=model,
    sorting_analyzer=analyzer,
    img_df=img_df,
    good_ids=good_ids,
    bad_ids=bad_ids,
    features=features
)
```

## Troubleshooting

### Common Issues

**"Prompt file not found"**
- Check that you're editing files in the correct directory
- Ensure filenames match exactly (case-sensitive)

**"AI makes unexpected decisions"**
- Review prompt clarity
- Add few-shot examples
- Try different model (e.g., gpt-4.1 vs gpt-4o)
- Check if images are rendering correctly (`plot_units_with_features_df`)

**"Rate limit errors"**
- Reduce `num_workers` parameter
- Add delays between batches
- Use fewer reviewers (`num_reviewers=1`)

**"Inconsistent results with multiple reviewers"**
- This is expected for borderline units
- Review average_score to see confidence level
- Consider using `num_reviewers=5` for critical datasets

---

## See Also

- [API Reference](api-reference.md) - Function signatures and parameters
- [User Guide](user-guide.md) - General usage workflows
- [Tutorials](../tutorials/) - End-to-end notebook examples
- [SpikeInterface Documentation](https://spikeinterface.readthedocs.io/) - Underlying spike sorting framework

---

## Contributing

If you develop improved prompts or find effective prompt strategies, please consider contributing them back to the project!
