"""SpikeAgent - AI-powered assistant for spike sorting and neural data analysis."""

__version__ = "0.102.3"

# Import commonly used functions for easy access
from spikeagent.app.tool.si_custom import (
    create_unit_img_df,
    create_merge_img_df,
)

from spikeagent.curation.vlm_curation import (
    run_vlm_curation,
    plot_spike_images_with_result,
)

from spikeagent.curation.vlm_merge import (
    run_vlm_merge,
    plot_merge_results,
)

from spikeagent.app.tool.utils import get_model

__all__ = [
    # Version
    "__version__",
    # Image creation functions
    "create_unit_img_df",
    "create_merge_img_df",
    # VLM curation functions
    "run_vlm_curation",
    "plot_spike_images_with_result",
    # VLM merge functions
    "run_vlm_merge",
    "plot_merge_results",
    # Utility functions
    "get_model",
]

