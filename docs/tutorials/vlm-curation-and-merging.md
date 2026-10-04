# VLM Curation And Merging Tutorial

This tutorial demonstrates the programmatic VLM workflow for curation and merge analysis. The source notebook lives at `tutorials/VLM_curation_and_merging_tutorial.ipynb`.

## What The Tutorial Covers

1. Generate a synthetic ground-truth recording.
2. Run MountainSort4 to create an initial sorting result.
3. Compute the SpikeInterface analyzer extensions needed for visualization and metrics.
4. Generate diagnostic images for each unit.
5. Run VLM curation to classify units as **Good** or **Bad**.
6. Find candidate merge groups.
7. Run VLM merge analysis.
8. Apply reviewed curation and merge decisions.

## Setup

Install SpikeAgent and the sorter in an activated virtual environment:

```bash
python -m pip install -e .
python -m pip install mountainsort4
```

Configure `OPENAI_API_KEY` in the environment or a local `.env` file.

```python
from dotenv import load_dotenv
import spikeinterface.full as si
from spikeagent import (
    create_merge_img_df,
    create_unit_img_df,
    get_model,
    plot_merge_results,
    plot_spike_images_with_result,
    plot_units_with_features,
    run_vlm_curation,
    run_vlm_merge,
)

load_dotenv()
si.set_global_job_kwargs(n_jobs=-1)
```

## Generate And Sort Test Data

```python
rec0, gt_sorting0 = si.generate_ground_truth_recording(
    num_channels=50,
    durations=[30.0],
    seed=43,
    num_units=30,
)
rec0 = si.bandpass_filter(rec0, freq_min=300, freq_max=6000)

sorter_name = "mountainsort4"
sorting_folder = "./mountainsort4_sorting"
default_params = si.get_default_sorter_params(sorter_name)

sorting = si.run_sorter(
    sorter_name=sorter_name,
    recording=rec0,
    folder=sorting_folder,
    remove_existing_folder=False,
    **default_params,
)
```

## Create The SortingAnalyzer

```python
analyzer_folder = sorting_folder + "/sorting_analyzer.zarr"
sorting_analyzer = si.create_sorting_analyzer(
    sorting=sorting,
    recording=rec0,
    format="zarr",
    folder=analyzer_folder,
    overwrite=False,
)
```

These examples preserve existing output folders. On a later run, use a new
output path or load the saved sorting and analyzer instead of overwriting them.

Compute the extensions needed by the plotting and VLM workflows:

```python
extension_params = {
    "random_spikes": {"method": "uniform", "max_spikes_per_unit": 600},
    "waveforms": {"ms_before": 1.0, "ms_after": 2.0},
    "templates": {},
    "template_similarity": {},
    "spike_locations": {},
    "unit_locations": {},
    "isi_histograms": {"window_ms": 30, "bin_ms": 0.5, "method": "auto"},
    "correlograms": {"window_ms": 30, "bin_ms": 0.5, "method": "auto"},
    "spike_amplitudes": {},
    "noise_levels": {},
    "principal_components": {},
    "quality_metrics": {
        "metric_names": [
            "snr",
            "firing_rate",
            "isi_violation",
            "presence_ratio",
            "amplitude_cutoff",
            "amplitude_median",
            "l_ratio",
            "nearest_neighbor",
        ]
    },
}

for key, value in extension_params.items():
    extension = sorting_analyzer.get_extension(key)
    if extension is None or not value.items() <= extension.params.items():
        sorting_analyzer.compute(key, **value)
```

## Run VLM Curation

```python
features = [
    "waveform_single",
    "waveform_multi",
    "autocorr",
    "spike_locations",
    "amplitude_plot",
]

plot_units_with_features(
    sorting_analyzer,
    unit_ids=sorting_analyzer.unit_ids[:30],
    features=features,
)

unit_img_df = create_unit_img_df(
    sorting_analyzer,
    unit_ids=None,
    features=features,
    load_if_exists=False,
    save_folder=sorting_folder,
)

model = get_model("gpt-4o")
results_df = run_vlm_curation(
    model=model,
    sorting_analyzer=sorting_analyzer,
    img_df=unit_img_df,
    features=features,
    good_ids=[],
    bad_ids=[],
    with_metrics=True,
    metrics_list=["snr", "isi_violations_ratio", "nn_hit_rate", "l_ratio"],
)

plot_spike_images_with_result(results_df, unit_img_df, feature="waveform_single")
```

For few-shot classification, replace the empty `good_ids` and `bad_ids` lists
with units that you have inspected and labeled from this sorting result.

Apply reviewed bad-unit removals:

```python
bad_units = results_df.index[results_df["final_classification"] == "Bad"].tolist()
reviewed_bad_units = []
analyzer_curated = (
    sorting_analyzer.remove_units(remove_unit_ids=reviewed_bad_units)
    if reviewed_bad_units
    else sorting_analyzer
)
```

Populate `reviewed_bad_units` after inspecting the suggested `bad_units`, the
reasoning, and the `reviewer_*_class` columns. Failed reviews are labeled `Error`
in those columns and can be aggregated into a `Bad` final classification.

## Run VLM Merge Analysis

```python
from spikeinterface.curation import compute_merge_unit_groups

potential_merge_groups = compute_merge_unit_groups(
    analyzer_curated,
    preset=None,
    resolve_graph=False,
    steps=["template_similarity"],
    steps_params={"template_similarity": {"template_diff_thresh": 0.3}},
)

merge_features = ["crosscorrelograms", "amplitude_plot", "waveform_single"]
merge_results_df = None
if potential_merge_groups:
    merge_img_df = create_merge_img_df(
        analyzer_curated,
        unit_groups=potential_merge_groups,
        features=merge_features,
        load_if_exists=False,
        save_folder=sorting_folder,
    )

    model = get_model("gpt-4.1")
    merge_results_df = run_vlm_merge(
        model=model,
        merge_unit_groups=potential_merge_groups,
        img_df=merge_img_df,
        features=merge_features,
    )

    plot_merge_results(merge_results_df, merge_img_df)
else:
    print("No candidate merge groups found.")
```

## Apply Reviewed Merges

```python
from spikeinterface.curation.curation_tools import resolve_merging_graph

reviewed_merge_group_ids = []
merged_analyzer = analyzer_curated
if merge_results_df is not None and reviewed_merge_group_ids:
    merge_unit_pairs = [
        merge_results_df.loc[group_idx, "merge_units"]
        for group_idx in reviewed_merge_group_ids
    ]
    final_merge_groups = resolve_merging_graph(analyzer_curated.sorting, merge_unit_pairs)
    if final_merge_groups:
        merged_analyzer = analyzer_curated.merge_units(
            merge_unit_groups=final_merge_groups,
            sparsity_overlap=0,
        )
```

Populate `reviewed_merge_group_ids` only with result rows you have reviewed and
approved for merging. With no approved groups, the analyzer is left unchanged.

## Notes

- Live VLM calls require provider credentials and may incur cost.
- Model outputs can vary across model versions and runs.
- Review curation and merge recommendations before applying them to final results.
