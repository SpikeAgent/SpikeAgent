# Few-Shot Learning Integration for VLM Merge

## Overview
Successfully integrated few-shot learning capability into the VLM merge system, allowing users to provide good and bad merge examples to calibrate the model's decision-making.

## Implementation Summary

### 🎯 **Core Concept**
- **Good merge examples**: Show units that should be merged together
- **Bad merge examples**: Show units that should NOT be merged
- **Calibration**: VLM uses these examples as reference anchors for decision-making

### 🔧 **Technical Implementation**

#### **A. New Parameters**
```python
def run_vlm_merge(
    model, 
    merge_unit_groups, 
    img_df, 
    features=MODALITY, 
    good_merge_groups=[],    # 🆕 Good merge examples (group IDs)
    bad_merge_groups=[],     # 🆕 Bad merge examples (group IDs)  
    num_workers=50
):
```

#### **B. Few-Shot Message Creation**
- **Good examples**: "These are Good merge examples you must compare with"
- **Bad examples**: "These are Bad merge examples you must compare with"
- **Image inclusion**: Shows actual feature images from example groups

#### **C. Integration Points**
1. **Prompt enhancement**: Adds fewshot instruction to each modality prompt
2. **Message flow**: System prompt → Fewshot examples → Current assessment
3. **Feature-specific**: Each feature gets its own fewshot examples

### 📊 **Usage Examples**

#### **Basic Usage (No Few-Shot)**
```python
# Standard usage without examples
results_df = run_vlm_merge(
    model=model,
    merge_unit_groups=[[4, 5], [7, 8]],
    img_df=merge_img_df,
    features=["crosscorrelograms", "pca_clustering"]
)
```

#### **With Few-Shot Examples**
```python
# Enhanced usage with good and bad examples
results_df = run_vlm_merge(
    model=model,
    merge_unit_groups=[[4, 5], [7, 8], [10, 11]],  # Groups to assess
    img_df=merge_img_df,
    features=["crosscorrelograms", "pca_clustering"],
    good_merge_groups=[0, 2],    # 🟢 Examples that should merge
    bad_merge_groups=[1, 3]      # 🔴 Examples that should NOT merge
)
```

#### **Real-World Example**
```python
# After manual review, use previous decisions as examples
good_examples = [5, 12, 18]  # Groups you manually verified as good merges
bad_examples = [3, 7, 15]    # Groups you manually verified as bad merges

results_df = run_vlm_merge(
    model=model,
    merge_unit_groups=new_merge_candidates,
    img_df=merge_img_df,
    features=["crosscorrelograms", "amplitude_plot", "pca_clustering"],
    good_merge_groups=good_examples,
    bad_merge_groups=bad_examples,
    num_workers=50
)
```

### 🧠 **How It Works**

#### **Message Flow for Each Feature:**
1. **System Prompt**: Feature-specific analysis instructions
2. **Few-Shot Examples**: 
   - Good merge images: "Compare with these Good examples..."
   - Bad merge images: "Compare with these Bad examples..."
3. **Current Assessment**: "Assess this current group..."

#### **Example Message Structure:**
```
[SYSTEM] You are given crosscorrelograms between units...
         Use these examples as anchors to calibrate your decision-making...

[HUMAN] These are Good merge examples you must compare with
        [Image: Good example 1 CCG]
        [Image: Good example 2 CCG]

[HUMAN] These are Bad merge examples you must compare with  
        [Image: Bad example 1 CCG]
        [Image: Bad example 2 CCG]

[HUMAN] Assess the quality of this crosscorrelograms of unit list: [4, 5]
        [Image: Current group CCG]
```

### ✨ **Key Benefits**

#### **🎯 Improved Accuracy**
- **Calibration**: VLM learns from your specific dataset characteristics
- **Consistency**: Maintains decision criteria across similar cases
- **Context-aware**: Adapts to your particular recording conditions

#### **🔄 Iterative Improvement**
- **Feedback loop**: Use previous decisions to improve future ones
- **Domain adaptation**: Learns patterns specific to your data
- **Error reduction**: Fewer false positives/negatives over time

#### **🎨 Flexibility**
- **Optional**: Works without examples (backward compatible)
- **Selective**: Can provide examples for some features only
- **Scalable**: Add more examples as you review more data

### 📋 **Best Practices**

#### **Example Selection**
- **Clear cases**: Choose unambiguous good/bad examples
- **Representative**: Include variety of merge scenarios
- **Balanced**: Roughly equal numbers of good/bad examples
- **Quality**: Ensure example images are clear and informative

#### **Usage Strategy**
1. **Start simple**: Begin with clear, obvious examples
2. **Build library**: Accumulate examples over time
3. **Update regularly**: Refresh examples based on new insights
4. **Feature-specific**: Consider which features benefit most from examples

### 🚀 **Integration Status**
✅ **Parameter handling**: Added good/bad merge group parameters  
✅ **Few-shot prompts**: Created merge-specific fewshot instructions  
✅ **Message creation**: Implemented fewshot message generation  
✅ **Prompt integration**: Added fewshot to modality prompts  
✅ **Async processing**: Updated async flow to handle fewshot  
✅ **Backward compatibility**: Works with existing code  

## Result
The VLM merge system now supports few-shot learning, enabling users to provide good and bad merge examples that significantly improve decision-making accuracy and consistency. This makes the system more adaptive to specific datasets and user preferences.
