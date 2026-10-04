# API Reference

SpikeAgent exposes a small public convenience API from the top-level `spikeagent` package and more detailed functions in submodules.

Prefer importing stable workflow helpers from `spikeagent`:

```python
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
```

Use the focused pages in this section for details on curation, plotting, and model selection.
