#!/usr/bin/env python3
"""
Test script for curation modules with a vanilla sorting_analyzer.

This script:
1. Creates a synthetic recording and sorting using SpikeInterface
2. Creates a sorting_analyzer
3. Computes necessary extensions (waveforms, templates, correlograms, etc.)
4. Tests the curation functions
"""

import os
import sys
import numpy as np

# Add src to path (go up from tests/curation/ to root, then to src)
_root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, os.path.join(_root_dir, 'src'))

import spikeinterface as si
import spikeinterface.full as sifull
from spikeagent.app.tool.si_custom import create_unit_img_df
from spikeagent.curation.vlm_curation import run_vlm_curation
from spikeagent.app.tool.utils import get_model


def create_test_sorting_analyzer(num_units=10, duration_sec=10.0, num_channels=32, seed=42):
    """
    Create a synthetic sorting_analyzer for testing.
    
    Parameters
    ----------
    num_units : int
        Number of units to create
    duration_sec : float
        Duration of recording in seconds
    num_channels : int
        Number of channels
    seed : int
        Random seed for reproducibility
        
    Returns
    -------
    sorting_analyzer : SortingAnalyzer
        A sorting_analyzer with computed extensions
    """
    print(f"Creating synthetic recording with {num_units} units, {num_channels} channels, {duration_sec}s duration...")
    
    # Set random seed
    np.random.seed(seed)
    
    # Create synthetic recording
    recording, sorting = si.generate_ground_truth_recording(
        durations=[duration_sec],
        num_channels=num_channels,
        num_units=num_units,
        sampling_frequency=30000.0,
        noise_kwargs={'noise_levels': 5.0, 'strategy': 'on_the_fly'},
        seed=seed
    )
    
    print(f"Created recording: {recording}")
    print(f"Created sorting: {sorting}")
    print(f"Unit IDs: {sorting.unit_ids}")
    
    # Create sorting_analyzer
    print("\nCreating sorting_analyzer...")
    sorting_analyzer = si.create_sorting_analyzer(
        sorting=sorting,
        recording=recording,
        format="memory"
    )
    
    # Compute necessary extensions for curation
    print("\nComputing extensions...")
    
    # 1. Random spikes (required before waveforms)
    print("  - Computing random_spikes...")
    sorting_analyzer.compute("random_spikes")
    
    # 2. Waveforms (needed for waveform_single, waveform_multi)
    print("  - Computing waveforms...")
    sorting_analyzer.compute("waveforms", n_jobs=1, chunk_size=10000)
    
    # 3. Templates (needed for waveform_multi)
    print("  - Computing templates...")
    sorting_analyzer.compute("templates")
    
    # 4. Correlograms (needed for autocorr)
    print("  - Computing correlograms...")
    sorting_analyzer.compute("correlograms", window_ms=100.0, bin_ms=1.0)
    
    # 5. Spike locations (needed for spike_locations)
    print("  - Computing spike locations...")
    sorting_analyzer.compute("spike_locations", method="center_of_mass")
    
    # 6. Spike amplitudes (needed for amplitude_plot)
    print("  - Computing spike amplitudes...")
    sorting_analyzer.compute("spike_amplitudes")
    
    # 7. Noise levels (required before quality_metrics)
    print("  - Computing noise levels...")
    sorting_analyzer.compute("noise_levels")
    
    # 8. Quality metrics (optional, for with_metrics=True)
    print("  - Computing quality metrics...")
    sorting_analyzer.compute("quality_metrics")
    
    print("\n✓ All extensions computed!")
    available_exts = [ext for ext in sorting_analyzer.get_computable_extensions() if sorting_analyzer.has_extension(ext)]
    print(f"Available extensions: {available_exts}")
    
    return sorting_analyzer


def test_curation_imports():
    """Test that all curation modules can be imported."""
    print("\n" + "="*60)
    print("TEST 1: Testing curation module imports")
    print("="*60)
    
    try:
        from spikeagent.curation import (
            get_guidance_on_rigid_curation,
            get_guidance_on_vlm_curation,
            get_guidance_on_vlm_merge_analysis,
            get_guidance_on_save_final_results,
        )
        from spikeagent.curation.vlm_curation import run_vlm_curation, plot_spike_images_with_result
        from spikeagent.curation.vlm_merge import run_vlm_merge, plot_merge_results
        
        print("✓ All curation modules imported successfully!")
        return True
    except Exception as e:
        print(f"✗ Import failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_sorting_analyzer_creation():
    """Test creating a sorting_analyzer with all necessary extensions."""
    print("\n" + "="*60)
    print("TEST 2: Creating sorting_analyzer with extensions")
    print("="*60)
    
    try:
        sorting_analyzer = create_test_sorting_analyzer(num_units=5, duration_sec=5.0)
        
        # Verify extensions
        required_extensions = ['waveforms', 'templates', 'correlograms', 'spike_locations', 'spike_amplitudes', 'quality_metrics']
        available_extensions = [ext for ext in sorting_analyzer.get_computable_extensions() if sorting_analyzer.has_extension(ext)]
        
        print(f"\nRequired extensions: {required_extensions}")
        print(f"Available extensions: {available_extensions}")
        
        missing = [ext for ext in required_extensions if ext not in available_extensions]
        if missing:
            print(f"✗ Missing extensions: {missing}")
            return None
        else:
            print("✓ All required extensions are available!")
            return sorting_analyzer
            
    except Exception as e:
        print(f"✗ Failed to create sorting_analyzer: {e}")
        import traceback
        traceback.print_exc()
        return None


def test_create_unit_img_df(sorting_analyzer):
    """Test creating unit image dataframe."""
    print("\n" + "="*60)
    print("TEST 3: Creating unit image dataframe")
    print("="*60)
    
    try:
        # Test with a subset of features
        features = ["waveform_single", "autocorr"]
        unit_ids = list(sorting_analyzer.unit_ids[:3])  # Test with first 3 units
        
        print(f"Creating image dataframe for units {unit_ids} with features {features}...")
        
        img_df = create_unit_img_df(
            sorting_analyzer,
            unit_ids=unit_ids,
            features=features,
            load_if_exists=False,
            save_folder=None
        )
        
        print(f"✓ Created image dataframe with shape: {img_df.shape}")
        print(f"  Columns: {list(img_df.columns)}")
        print(f"  Index (unit_ids): {list(img_df.index)}")
        
        # Verify the dataframe has the expected structure
        assert len(img_df) == len(unit_ids), "Dataframe should have one row per unit"
        assert all(feat in img_df.columns for feat in features), "All features should be in columns"
        
        print("✓ Image dataframe structure is correct!")
        return img_df
        
    except Exception as e:
        print(f"✗ Failed to create image dataframe: {e}")
        import traceback
        traceback.print_exc()
        return None


def test_rigid_curation(sorting_analyzer):
    """Test rigid curation (threshold-based)."""
    print("\n" + "="*60)
    print("TEST 4: Testing rigid curation")
    print("="*60)
    
    try:
        # Get quality metrics
        metrics = sorting_analyzer.get_extension('quality_metrics').get_data()
        print(f"Quality metrics shape: {metrics.shape}")
        print(f"Available metrics: {list(metrics.columns)}")
        
        # Apply rigid curation with reasonable thresholds
        min_snr = 2.0
        max_isi = 5.0  # 5% ISI violations
        
        query = f"(snr > {min_snr}) & (isi_violations_ratio < {max_isi}) & (presence_ratio > 0.9)"
        good_units = metrics.query(query).index.values
        
        print(f"\nApplied query: {query}")
        print(f"Found {len(good_units)} good units: {list(good_units)}")
        
        if len(good_units) > 0:
            curated_analyzer = sorting_analyzer.select_units(good_units)
            print(f"✓ Created curated analyzer with {len(curated_analyzer.unit_ids)} units")
            return curated_analyzer
        else:
            print("⚠ No units passed the thresholds (this is okay for synthetic data)")
            return None
            
    except Exception as e:
        print(f"✗ Rigid curation failed: {e}")
        import traceback
        traceback.print_exc()
        return None


def test_vlm_curation_structure(sorting_analyzer, img_df):
    """Test VLM curation structure (without actually calling the model)."""
    print("\n" + "="*60)
    print("TEST 5: Testing VLM curation structure")
    print("="*60)
    
    try:
        # Check that we can access the function
        from spikeagent.curation.vlm_curation import run_vlm_curation
        
        print("✓ VLM curation function is accessible")
        
        # Check function signature
        import inspect
        sig = inspect.signature(run_vlm_curation)
        print(f"Function signature: {sig}")
        
        # Verify we have the required data
        print(f"\nSorting analyzer has {len(sorting_analyzer.unit_ids)} units")
        print(f"Image dataframe has {len(img_df)} units")
        
        # Check that img_df has the right structure
        required_features = ["waveform_single", "autocorr"]
        for feat in required_features:
            if feat in img_df.columns:
                print(f"✓ Feature '{feat}' found in image dataframe")
            else:
                print(f"✗ Feature '{feat}' missing in image dataframe")
                return False
        
        print("\n✓ VLM curation structure is correct!")
        print("  (Note: Actual VLM call requires API keys and would make API calls)")
        
        return True
        
    except Exception as e:
        print(f"✗ VLM curation structure test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_curation_guidance_functions():
    """Test that the guidance functions can be called."""
    print("\n" + "="*60)
    print("TEST 6: Testing curation guidance functions")
    print("="*60)
    
    try:
        from spikeagent.curation import (
            get_guidance_on_rigid_curation,
            get_guidance_on_vlm_curation,
        )
        
        # Test rigid curation guidance
        reasoning = "Testing rigid curation with SNR > 2.0 and ISI < 5%"
        code = """
        metrics = sorting_analyzer.get_extension('quality_metrics').get_data()
        query = "(snr > 2.0) & (isi_violations_ratio < 5.0) & (presence_ratio > 0.9)"
        good_units = metrics.query(query).index.values
        curated_analyzer = sorting_analyzer.select_units(good_units)
        """
        
        result = get_guidance_on_rigid_curation(reasoning, code)
        print(f"✓ get_guidance_on_rigid_curation returned {len(result)} characters")
        
        # Test VLM curation guidance
        reasoning = "Testing VLM curation with waveform_single and autocorr"
        code = """
        from spikeagent.curation.vlm_curation import run_vlm_curation
        # ... (template code)
        """
        
        result = get_guidance_on_vlm_curation(reasoning, code)
        print(f"✓ get_guidance_on_vlm_curation returned {len(result)} characters")
        
        print("\n✓ All guidance functions work correctly!")
        return True
        
    except Exception as e:
        print(f"✗ Guidance functions test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("="*60)
    print("CURATION MODULES TEST SUITE")
    print("="*60)
    print("\nThis script tests the curation modules with a synthetic sorting_analyzer.")
    print("Note: VLM curation will be tested for structure only (no API calls).\n")
    
    results = {}
    
    # Test 1: Imports
    results['imports'] = test_curation_imports()
    
    # Test 2: Create sorting_analyzer
    sorting_analyzer = test_sorting_analyzer_creation()
    results['sorting_analyzer'] = sorting_analyzer is not None
    
    if sorting_analyzer is None:
        print("\n✗ Cannot continue without sorting_analyzer. Exiting.")
        return
    
    # Test 3: Create image dataframe
    img_df = test_create_unit_img_df(sorting_analyzer)
    results['img_df'] = img_df is not None
    
    # Test 4: Rigid curation
    results['rigid_curation'] = test_rigid_curation(sorting_analyzer) is not None
    
    # Test 5: VLM curation structure
    if img_df is not None:
        results['vlm_structure'] = test_vlm_curation_structure(sorting_analyzer, img_df)
    else:
        results['vlm_structure'] = False
    
    # Test 6: Guidance functions
    results['guidance'] = test_curation_guidance_functions()
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    for test_name, passed in results.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    total = len(results)
    passed = sum(results.values())
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed!")
        return 0
    else:
        print(f"\n⚠ {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)

