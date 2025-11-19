# Waveform Single Prompt Improvements

## Problem
The original waveform_single prompt was **too permissive** and almost always approved merges, making it non-discriminative and unhelpful for decision making.

## Root Cause Analysis
The original prompt had several issues:
1. **Default to merge**: "If all units appear similar, approve merge"
2. **Vague criteria**: "identify only clear outliers"
3. **No specific guidelines**: Lacked concrete morphological criteria
4. **No conservative bias**: No guidance for ambiguous cases

## Key Improvements

### 1. **Balanced Decision Framework**
- **Before**: Default to merge unless "clear outliers"
- **After**: Requires ALL criteria to be met for merge approval

### 2. **Specific Morphological Criteria**
Added detailed requirements for merge approval:
- Peak alignment (±0.1ms tolerance)
- Morphological consistency (shape, width, kinetics)
- Baseline stability
- Triphasic pattern consistency
- Temporal feature matching

### 3. **Clear Rejection Criteria**
Specific conditions that should prevent merging:
- Peak misalignment
- Shape inconsistencies 
- Kinetic differences (rise/decay times)
- Baseline drift patterns
- Artifact signatures

### 4. **Conservative Decision Bias**
- Added explicit guidance: "When in doubt, DO NOT merge"
- "It's better to be conservative"
- Emphasized that similarity ≠ automatic merge

### 5. **Structured Analysis Approach**
1. **Overlay Assessment**: Mental overlay of waveforms
2. **Feature Comparison**: Systematic feature-by-feature analysis
3. **Consistency Check**: Look for systematic differences

## Expected Impact

### Before (Problematic)
```
✓ Units look similar → Always merge
✓ Passed threshold → Always merge
✓ No obvious outliers → Always merge
```

### After (Balanced)
```
✓ Peak alignment AND
✓ Shape consistency AND  
✓ Kinetic matching AND
✓ Baseline stability → Consider merge

❌ Any systematic differences → Do NOT merge
❌ Ambiguous case → Do NOT merge (conservative)
```

## Validation Metrics
- Prompt length: 2,226 characters (vs ~400 before)
- Contains balanced merge/reject criteria
- Includes conservative decision guidance
- Provides specific morphological criteria

## Usage Notes
- The improved prompt should reduce false positive merges
- It maintains sensitivity to genuine merge candidates
- The conservative bias helps prevent over-merging
- Works within the existing VLM merge hierarchical decision system (CCG still has priority)

This improvement addresses the core issue of the waveform analysis being too permissive while maintaining the ability to identify genuine merge candidates.
