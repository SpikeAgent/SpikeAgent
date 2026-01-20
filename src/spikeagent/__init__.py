"""SpikeAgent - AI-powered assistant for spike sorting and neural data analysis."""

__version__ = "0.102.3"

from .curation.vlm_curation import run_vlm_curation, plot_spike_images_with_result
from .curation.vlm_merge import run_vlm_merge, plot_merge_results
from .app.tool.si_custom import create_unit_img_df, create_merge_img_df, plot_units_with_features
from .app.tool.utils import get_model

__all__ = [
    "run_vlm_curation",
    "plot_spike_images_with_result",
    "run_vlm_merge",
    "plot_merge_results",
    "create_unit_img_df",
    "create_merge_img_df",
    "get_model",
    "plot_units_with_features"
]
