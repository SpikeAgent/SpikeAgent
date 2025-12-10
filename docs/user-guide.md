# User Guide

This guide explains how to use SpikeAgent for spike sorting and neural data analysis.

## Overview

SpikeAgent is a web-based AI assistant that helps you:
- Perform spike sorting on neural recordings
- Curate and validate sorted units
- Analyze spike sorting results using Vision-Language Models (VLM)
- Merge units that belong to the same neuron

## Getting Started

### 1. Launch SpikeAgent

After installation, start the Docker container and open `http://localhost:8501` in your browser.

### 2. Select an AI Provider

In the left sidebar, choose one of the available AI providers:
- **OpenAI** (GPT-4o)
- **Anthropic** (Claude)
- **Google** (Gemini)

### 3. Start a Conversation

Type your question or request in the chat interface. SpikeAgent can help with:
- Loading and preprocessing recordings
- Running spike sorters
- Curation workflows
- Data analysis

## Common Workflows

### Loading Data

Ask SpikeAgent to load your neural recording:

```
Load my recording from /path/to/recording
```

SpikeAgent supports various formats including:
- Intan `.rhd` files
- Neuropixels data
- Other formats supported by SpikeInterface

### Spike Sorting

Request spike sorting:

```
Run spike sorting on my recording using Kilosort4
```

SpikeAgent will:
1. Check if the required sorter is available
2. Configure sorting parameters
3. Run the sorting algorithm
4. Display results

### Curation

Use AI-assisted curation:

```
Curate the sorted units using VLM
```

This will:
1. Generate visualizations for each unit
2. Use Vision-Language Models to classify units
3. Filter out noise units
4. Create a curated sorting result

### Merge Analysis

Find and merge duplicate units:

```
Find units that should be merged
```

SpikeAgent will:
1. Identify potential merge candidates
2. Analyze visual features using VLM
3. Recommend merges
4. Apply merges if confirmed

## Advanced Features

### VLM Curation

Vision-Language Models can classify units as "Good" or "Bad" based on:
- Waveform shapes
- Autocorrelograms
- Spike locations
- Amplitude distributions
- Quality metrics

### VLM Merge Analysis

AI can determine if units should be merged by analyzing:
- Cross-correlograms
- Waveform similarity
- Spatial locations
- PCA clustering
- Amplitude distributions

## Tips and Best Practices

1. **Start with small datasets**: Test workflows on small recordings first
2. **Save frequently**: SpikeAgent can save intermediate results
3. **Review VLM decisions**: Always review AI classifications before finalizing
4. **Use appropriate sorters**: Some sorters require GPU support
5. **Check quality metrics**: Review quantitative metrics alongside visual analysis

## Troubleshooting

### Common Issues

**"No recording loaded"**
- Ensure your data path is correct
- Check that the file format is supported

**"Sorter not found"**
- Verify the sorter is installed
- For GPU sorters, ensure you're using the GPU Docker image

**"VLM analysis failed"**
- Check your API keys are valid
- Verify you have API credits/quota remaining

**"Memory errors"**
- Reduce the size of your recording
- Use a machine with more RAM
- Consider processing in chunks

## Next Steps

- Explore the [Jupyter notebook tutorials](../tutorials/) for detailed examples
- Read the [API Reference](api-reference.md) for programmatic usage
- Check the [FAQ](faq.md) for common questions

