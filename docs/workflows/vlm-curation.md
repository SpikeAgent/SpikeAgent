# VLM Curation

VLM curation classifies sorted units as **Good** or **Bad** by analyzing diagnostic unit plots and optional quality metrics.

## Inputs

- A SpikeInterface `SortingAnalyzer`.
- A DataFrame of base64-encoded unit images from `create_unit_img_df`.
- A vision-capable chat model from `get_model`.
- Optional few-shot example unit IDs.
- Optional quality metrics such as `snr`, `isi_violations_ratio`, and `l_ratio`.

## Minimal Example

```python
from spikeagent import create_unit_img_df, get_model, run_vlm_curation

features = ["waveform_single", "autocorr", "spike_locations"]
img_df = create_unit_img_df(sorting_analyzer, features=features)

model = get_model("gpt-4o")
results = run_vlm_curation(
    model=model,
    sorting_analyzer=sorting_analyzer,
    img_df=img_df,
    features=features,
    with_metrics=True,
    metrics_list=["snr", "isi_violations_ratio", "l_ratio"],
)

good_unit_ids = results[results["final_classification"] == "Good"].index.tolist()
curated_analyzer = sorting_analyzer.remove_units(
    remove_unit_ids=[
        unit_id for unit_id in sorting_analyzer.unit_ids if unit_id not in good_unit_ids
    ]
)
```

## Human Review

VLM outputs should be reviewed before applying final curation. The result DataFrame includes classifications, scores, and reasoning to support that review.
