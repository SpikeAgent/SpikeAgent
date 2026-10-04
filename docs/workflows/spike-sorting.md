# Spike Sorting Workflow

SpikeAgent guides users through a SpikeInterface-based spike sorting workflow from recordings to curated sorting results.

## Typical Flow

1. Load a recording from disk.
2. Inspect recording metadata and signal quality.
3. Apply preprocessing such as filtering and referencing.
4. Run a spike sorter.
5. Compute analyzer extensions for waveforms, metrics, correlograms, amplitudes, and locations.
6. Review diagnostic plots.
7. Apply curation and merge decisions.
8. Save final results.

## Interactive App

In the Streamlit app, describe the workflow in plain language:

```text
Load my recording from /path/to/recording and inspect it for spike sorting.
```

SpikeAgent uses tool-guided responses to suggest code, run analysis steps, render plots, and ask for confirmation before high-impact workflow transitions.

## Programmatic Workflows

Programmatic workflows should build around SpikeInterface objects such as recordings, sortings, and sorting analyzers. The VLM APIs expect diagnostic images and relevant analyzer extensions to already exist.
