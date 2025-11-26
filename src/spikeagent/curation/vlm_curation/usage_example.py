#!/usr/bin/env python3
"""
Usage example for the flexible metrics VLM curation system.
"""

from run_vlm import run_vlm_curation

def example_usage():
    """
    Example of how to use the new flexible metrics functionality
    """
    
    # Example 1: Using default metrics (backward compatibility)
    print("Example 1: Default metrics")
    """
    results_df = run_vlm_curation(
        model=your_model,
        sorting_analyzer=your_sorting_analyzer,
        img_df=your_img_df,
        features=["waveform_single", "autocorr", "spike_locations"],
        with_metrics=True  # Uses default: ["snr", "isi_violations_ratio", "l_ratio"]
    )
    """
    
    # Example 2: Custom metrics selection
    print("\nExample 2: Custom metrics selection")
    """
    results_df = run_vlm_curation(
        model=your_model,
        sorting_analyzer=your_sorting_analyzer,
        img_df=your_img_df,
        features=["waveform_single", "waveform_multi", "autocorr"],
        with_metrics=True,
        metrics_list=["snr", "nn_hit_rate", "amplitude_cutoff", "presence_ratio"]
    )
    """
    
    # Example 3: Single metric
    print("\nExample 3: Single metric")
    """
    results_df = run_vlm_curation(
        model=your_model,
        sorting_analyzer=your_sorting_analyzer,
        img_df=your_img_df,
        features=["waveform_single"],
        with_metrics=True,
        metrics_list=["nn_hit_rate"]  # Only assess NN hit rate
    )
    """
    
    # Example 4: All available features and many metrics
    print("\nExample 4: Comprehensive assessment")
    """
    results_df = run_vlm_curation(
        model=your_model,
        sorting_analyzer=your_sorting_analyzer,
        img_df=your_img_df,
        features=["waveform_single", "waveform_multi", "autocorr", "spike_locations", "amplitude_plot"],
        with_metrics=True,
        metrics_list=["snr", "isi_violations_ratio", "l_ratio", "nn_hit_rate", "amplitude_cutoff", "presence_ratio"],
        good_ids=[1, 5, 10],  # Examples of good units for few-shot learning
        bad_ids=[2, 8],       # Examples of bad units for few-shot learning
        unit_ids=None,        # Process all units
        num_workers=50
    )
    """
    
    print("\nKey benefits of the flexible metrics system:")
    print("1. Choose only the metrics relevant to your analysis")
    print("2. Prompts automatically adapt to include descriptions of selected metrics")
    print("3. Backward compatibility with existing code")
    print("4. Easy to add new metrics by creating prompt files")
    print("5. Graceful handling of missing or invalid metrics")

if __name__ == "__main__":
    example_usage()
