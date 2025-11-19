# Head.txt Prompt Improvements

## Problem Addressed
The original head.txt prompt had unclear priority logic and didn't properly handle cases where other modalities show clear issues that should override merge decisions.

## Key Improvements

### 1. **🔴 IMMEDIATE REJECTION CRITERIA** (New Feature)
Added safety net that allows ANY modality to immediately reject a merge:
- **CCG**: Clear spikes in refractory period (±1.5ms)
- **Waveform**: Systematic morphological differences  
- **Spatial**: Units spatially separated beyond reasonable drift
- **Amplitude**: Completely non-overlapping distributions

This addresses your concern about other modalities being able to reject merges when they show clear issues.

### 2. **🟡 HIERARCHICAL ASSESSMENT** (Improved)
Clearer priority structure:
1. **CCG as Primary Evidence** (maintains CCG priority)
2. **Secondary Evidence Integration** (when CCG is ambiguous)
3. **Conservative Principle** (default to not merge when uncertain)

### 3. **⚖️ CONFLICT RESOLUTION** (New Feature)
Specific guidance for handling conflicts:
- **CCG vs Others**: Investigate carefully when CCG supports but others object
- **Multiple concerns**: If 2+ modalities raise issues, favor NOT merging
- **Borderline cases**: Default to NOT merge

### 4. **Multi-Modality Support** (Enhanced)
Now properly considers all modalities:
- Cross-correlograms (CCG) - Primary
- Waveform analysis - Secondary
- Amplitude analysis - Secondary  
- Spatial locations - Secondary

## Before vs After

### Before (Problems)
```
❌ Only mentioned CCG and amplitude
❌ Unclear when other modalities can override
❌ Confusing syntax and formatting
❌ No safety nets for clear red flags
❌ Ambiguous conflict resolution
```

### After (Solutions)
```
✅ All modalities can immediately reject merges for clear issues
✅ Clear hierarchy: CCG primary, others secondary
✅ Explicit override conditions
✅ Conservative default (better false negative than false positive)
✅ Structured conflict resolution rules
✅ Clean formatting with clear sections
```

## Decision Logic Flow

1. **🔴 Check for Immediate Rejection**: Any modality showing clear neurophysiological incompatibility?
   - **YES** → Reject merge immediately
   - **NO** → Continue to hierarchical assessment

2. **🟡 Hierarchical Assessment**:
   - **CCG Strong Support** + No contradictions → Merge
   - **CCG Ambiguous** → Consult secondary evidence
   - **CCG Weak/No Support** → Likely no merge unless strong secondary evidence

3. **⚖️ Conflict Resolution**:
   - Multiple modalities concerned → No merge
   - Borderline case → No merge (conservative)

## Expected Benefits

1. **Safety**: Prevents merges when any modality shows clear issues
2. **Clarity**: Clear decision hierarchy and conflict resolution
3. **Balance**: Maintains CCG priority while allowing other modalities to have veto power
4. **Conservative**: Defaults to not merging in ambiguous cases
5. **Comprehensive**: Considers all available evidence systematically

This improved prompt should address your concern about other modalities being able to reject merges when they identify clear issues, while still maintaining the appropriate priority for CCG analysis.
