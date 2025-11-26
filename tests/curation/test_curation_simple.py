#!/usr/bin/env python3
"""
Quick test for curation modules - minimal version.

This creates a simple sorting_analyzer and tests basic functionality.
"""

import os
import sys

# Add src to path (go up from tests/curation/ to root, then to src)
_root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, os.path.join(_root_dir, 'src'))

import spikeinterface as si
import spikeinterface.full as sifull
from spikeagent.app.tool.si_custom import create_unit_img_df


def quick_test():
    """Quick test of curation modules."""
    print("Creating synthetic sorting_analyzer...")
    
    # Create simple synthetic data
    recording, sorting = si.generate_ground_truth_recording(
        durations=[5.0],
        num_channels=16,
        num_units=5,
        sampling_frequency=30000.0,
        noise_kwargs={'noise_levels': 5.0, 'strategy': 'on_the_fly'},
        seed=42
    )
    
    # Create sorting_analyzer
    sorting_analyzer = si.create_sorting_analyzer(
        sorting=sorting,
        recording=recording,
        format="memory"
    )
    
    print(f"✓ Created sorting_analyzer with {len(sorting_analyzer.unit_ids)} units")
    
    # Compute minimal extensions needed for testing
    print("Computing extensions...")
    sorting_analyzer.compute("random_spikes")  # Required before waveforms
    sorting_analyzer.compute("waveforms", n_jobs=1)
    sorting_analyzer.compute("templates")
    sorting_analyzer.compute("correlograms", window_ms=100.0, bin_ms=1.0)
    sorting_analyzer.compute("spike_locations", method="center_of_mass")
    sorting_analyzer.compute("spike_amplitudes")
    sorting_analyzer.compute("noise_levels")  # Required before quality_metrics
    sorting_analyzer.compute("quality_metrics")
    
    available_exts = [ext for ext in sorting_analyzer.get_computable_extensions() if sorting_analyzer.has_extension(ext)]
    print(f"✓ Extensions computed: {available_exts}")
    
    # Test creating image dataframe
    print("\nTesting image dataframe creation...")
    import tempfile
    with tempfile.TemporaryDirectory() as tmpdir:
        img_df = create_unit_img_df(
            sorting_analyzer,
            unit_ids=list(sorting_analyzer.unit_ids[:3]),
            features=["waveform_single", "autocorr"],
            load_if_exists=False,
            save_folder=tmpdir
        )
    
    print(f"✓ Image dataframe created: {img_df.shape}")
    print(f"  Units: {list(img_df.index)}")
    print(f"  Features: {list(img_df.columns)}")
    
    # Test rigid curation
    print("\nTesting rigid curation...")
    metrics = sorting_analyzer.get_extension('quality_metrics').get_data()
    good_units = metrics.query("snr > 1.0 & isi_violations_ratio < 10.0").index.tolist()
    print(f"✓ Found {len(good_units)} good units: {good_units}")
    
    if len(good_units) > 0:
        curated = sorting_analyzer.select_units(good_units)
        print(f"✓ Created curated analyzer with {len(curated.unit_ids)} units")
    
    # Test imports
    print("\nTesting curation module imports...")
    from spikeagent.curation import (
        get_guidance_on_rigid_curation,
        get_guidance_on_vlm_curation,
    )
    from spikeagent.curation.vlm_curation import run_vlm_curation
    print("✓ All curation modules imported successfully")
    
    print("\n" + "="*60)
    print("✓ All basic tests passed!")
    print("="*60)
    print("\nThe sorting_analyzer is ready for curation!")
    print(f"  - {len(sorting_analyzer.unit_ids)} units available")
    print(f"  - All required extensions computed")
    print(f"  - Image dataframe can be created")
    print("\nTo test VLM curation, you would need:")
    print("  - API keys (OpenAI, Anthropic, or Google)")
    print("  - Call run_vlm_curation() with a model")
    
    return sorting_analyzer, img_df


if __name__ == "__main__":
    try:
        sorting_analyzer, img_df = quick_test()
    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

