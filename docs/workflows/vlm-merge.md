# VLM Merge Analysis

VLM merge analysis evaluates candidate groups of units that may represent the same neuron.

## Inputs

- A curated or partially curated `SortingAnalyzer`.
- Candidate merge groups, often generated with `spikeinterface.curation.compute_merge_unit_groups`.
- A DataFrame of base64-encoded comparison images from `create_merge_img_df`.
- A vision-capable chat model from `get_model`.

## Minimal Example

```python
from spikeinterface.curation import compute_merge_unit_groups
from spikeagent import create_merge_img_df, get_model, run_vlm_merge

merge_groups = compute_merge_unit_groups(
    sorting_analyzer,
    resolve_graph=False,
    steps=["template_similarity"],
    steps_params={"template_similarity": {"template_diff_thresh": 0.3}},
)

features = ["crosscorrelograms", "amplitude_plot", "waveform_single"]
img_df = create_merge_img_df(
    sorting_analyzer,
    unit_groups=merge_groups,
    features=features,
)

model = get_model("gpt-4.1")
results = run_vlm_merge(
    model=model,
    merge_unit_groups=merge_groups,
    img_df=img_df,
    features=features,
)
```

## Review Criteria

The VLM considers waveform similarity, cross-correlograms, amplitude distributions, and other visual evidence. Treat the output as a recommendation and apply merges only after review.
