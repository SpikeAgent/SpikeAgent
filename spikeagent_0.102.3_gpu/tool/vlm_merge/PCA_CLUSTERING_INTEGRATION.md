# PCA Clustering Integration for VLM Merge

## Overview
Successfully integrated PCA clustering analysis into the VLM merge system to prevent over-merging by detecting when units form distinct clusters versus continuous distributions in PCA space.

## Implementation Summary

### 1. **🎯 Core Concept**
- **Same neuron**: Should show **continuous, overlapping distribution** in PCA space
- **Different neurons**: Form **distinct, separated clusters** with gaps
- **Critical for preventing over-merging**: Identifies cases where units look similar but are actually from different neurons

### 2. **🔧 Technical Implementation**

#### **A. Plot Function** (`custom_plot.py`)
```python
def plot_pca_clustering(sortinganalyzer, unit_ids=None, unit_colors=None, title="PCA Clustering", figsize=(8, 8))
```

**Features:**
- **Dual-panel visualization**: Individual units (left) + combined density (right)
- **Balanced sampling**: Subsamples larger units to match smaller ones (prevents bias)
- **Smoothed density**: Gaussian filtering for clearer pattern identification
- **Robust plotting**: Percentile-based range estimation for outlier handling

#### **B. Integration Points**
1. **MERGE_FEATURES**: Added `"pca_clustering"` to available features
2. **VLM modalities**: Added to `MODALITY` list in `run_vlm.py`
3. **Feature mapping**: Integrated into `create_merge_img_df` pipeline
4. **Caption mapping**: Added descriptive text for VLM processing

#### **C. VLM Analysis System**
1. **Prompt creation**: `prompts/modality/pca_clustering.txt`
2. **Decision integration**: Updated `head.txt` for hierarchical analysis
3. **Immediate rejection**: PCA can now veto merges when showing clear clusters

### 3. **🧠 VLM Assessment Strategy**

#### **PCA Clustering Prompt Analysis**
```
✅ Support Merge if:
- Continuous distribution with significant overlap
- Single main peak in combined density
- Gradual transitions between units
- Shared density regions

❌ Do NOT merge if:
- Distinct clusters with clear gaps
- Bimodal/multimodal density peaks
- Sharp boundaries between units
- Isolated populations
```

#### **Integration with Decision Hierarchy**
1. **🔴 Immediate Rejection**: PCA can override all other evidence
2. **🟡 Secondary Evidence**: PCA continuity supports ambiguous CCG cases
3. **⚖️ Conflict Resolution**: Multiple modality concerns include PCA

### 4. **📊 Visual Analysis Structure**

#### **Left Panel: Individual Units**
- Scatter plot showing each unit in different colors
- Assesses spatial separation and overlap
- Identifies isolated clusters or continuous distributions

#### **Right Panel: Combined Density**
- Smoothed histogram of all units combined
- Reveals overall distribution patterns
- Shows whether merge would create natural or artificial distribution

### 5. **🔑 Key Decision Principles**

#### **Clustering Indicators**
- **Cluster separation**: Visible gaps between unit distributions
- **Density continuity**: Single peak vs multiple distinct peaks
- **Overlap assessment**: How much units share the same space
- **Spatial distribution**: Scattered together vs separated groups

#### **Conservative Approach**
- **When ambiguous**: Lean towards NOT merging
- **Systematic separation**: Look for consistent patterns, not random scatter
- **Overall pattern**: Consider general distribution shape over outliers

### 6. **📈 Expected Benefits**

#### **Prevents Over-merging**
- Catches cases where units pass template similarity but are actually different neurons
- Provides dimensionality-reduced view that reveals separation not visible in raw waveforms
- Balances spike count differences that might bias other analyses

#### **Complements Existing Modalities**
- **CCG**: Temporal relationships (primary)
- **Waveforms**: Morphological similarity
- **Amplitude**: Signal strength consistency  
- **PCA**: High-dimensional feature space separation (**NEW**)

### 7. **🚀 Usage Examples**

#### **Basic Usage**
```python
# Include PCA clustering in merge analysis
merge_results_df = run_vlm_merge(
    model=model,
    merge_unit_groups=potential_merge_groups,
    img_df=merge_img_df,
    features=["crosscorrelograms", "amplitude_plot", "pca_clustering"],  # NEW
    num_workers=50
)
```

#### **PCA-focused Analysis**
```python
# Focus on PCA for difficult cases
features=["crosscorrelograms", "pca_clustering"]  # Minimal but powerful combo
```

### 8. **⚠️ Requirements**
- **Principal Components extension**: Must be computed on sorting analyzer
- **At least 2 units**: PCA clustering needs comparison between units
- **Sufficient spikes**: Each unit should have enough spikes for meaningful analysis

### 9. **🔄 Integration Status**
✅ **Plot function**: `plot_pca_clustering()` implemented  
✅ **Feature mapping**: Added to `create_merge_img_df`  
✅ **VLM prompts**: Created `pca_clustering.txt`  
✅ **Decision logic**: Updated `head.txt` hierarchy  
✅ **Modality lists**: Updated across all files  
✅ **Testing**: Integration verified  

## Result
The VLM merge system now has a powerful tool to prevent over-merging by analyzing high-dimensional feature relationships that might not be apparent in other modalities. This addresses the specific concern about units that pass similarity thresholds but should not be merged due to distinct clustering in PCA space.
