# VLM Curation

VLM curation classifies sorted units as **Good** or **Bad** by analyzing diagnostic unit plots and optional quality metrics.

## Inputs

- A SpikeInterface `SortingAnalyzer`.
- A DataFrame of base64-encoded unit images from `create_unit_img_df`.
- A vision-capable chat model from `get_model`.
- Optional few-shot example unit IDs.
- Optional quality metrics such as `snr`, `isi_violations_ratio`, and `l_ratio`.

The example requires `templates`, `correlograms`, `spike_locations`, and
`quality_metrics` to be computed on the analyzer first.

## Minimal Example

```python
from dotenv import load_dotenv
from spikeagent import create_unit_img_df, get_model, run_vlm_curation

load_dotenv()
features = ["waveform_single", "autocorr", "spike_locations"]
img_df = create_unit_img_df(
    sorting_analyzer, features=features, load_if_exists=False
)

model = get_model("gpt-4o")
results = run_vlm_curation(
    model=model,
    sorting_analyzer=sorting_analyzer,
    img_df=img_df,
    features=features,
    with_metrics=True,
    metrics_list=["snr", "isi_violations_ratio", "l_ratio"],
)

print(results[["final_classification", "average_score", "combined_reasoning"]])
```

## Human Review

VLM outputs should be reviewed before applying final curation. The result DataFrame includes classifications, scores, and reasoning to support that review.

Inspect the `reviewer_*_class` columns for failed reviews labeled `Error`; the
current aggregation can classify these units as `Bad`. Keep those units for
manual review or retry the failed calls before deciding which units to remove.

After reviewing the results, set the unit IDs to remove explicitly:

```python
reviewed_bad_unit_ids = []
curated_analyzer = (
    sorting_analyzer.remove_units(remove_unit_ids=reviewed_bad_unit_ids)
    if reviewed_bad_unit_ids
    else sorting_analyzer
)
```
