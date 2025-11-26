from langchain_core.prompts import SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain_core.prompts import ChatPromptTemplate
import os

current = os.path.dirname(os.path.abspath(__file__))

def load_prompt(path: str) -> str:
    with open(path, 'r') as f:
        return f.read().strip()

def load_all_prompts():
    base_path = f"{current}/prompts"
    modality_path = f"{base_path}/modality"
    
    return {
        "head": load_prompt(f"{base_path}/head.txt"),
        "modality": {
            "waveform_single": load_prompt(f"{modality_path}/waveform_single.txt"),
            "waveform_multi": load_prompt(f"{modality_path}/waveform_multi.txt"),
            "autocorr": load_prompt(f"{modality_path}/autocorr.txt"),
            "spike_locations": load_prompt(f"{modality_path}/spike_locations.txt"),
            "amplitude_plot": load_prompt(f"{modality_path}/amplitude_plot.txt"),
        },
        "metrics": load_prompt(f"{base_path}/metrics.txt"),  # Keep for backward compatibility
        "metrics_header": load_prompt(f"{base_path}/metrics_header.txt"),
        "fewshot": load_prompt(f"{base_path}/fewshot_instruction.txt"),
    }

def load_metrics_prompts(metrics_list):
    """Load individual metric prompt files and combine them"""
    base_path = f"{current}/prompts"
    metrics_path = f"{base_path}/metrics"
    
    metrics_descriptions = []
    available_metric_files = []
    
    # Check which metric files exist
    for metric in metrics_list:
        metric_file = f"{metrics_path}/{metric}.txt"
        if os.path.exists(metric_file):
            available_metric_files.append(metric)
            metrics_descriptions.append(load_prompt(metric_file))
        else:
            print(f"Warning: No prompt file found for metric '{metric}' at {metric_file}")
    
    if not metrics_descriptions:
        # Fallback to original metrics prompt if no individual files found
        print("No individual metric prompt files found, using default metrics prompt")
        return load_prompt(f"{base_path}/metrics.txt")
    
    # Load header and format with metric descriptions
    header = load_prompt(f"{base_path}/metrics_header.txt")
    combined_descriptions = "\n\n".join(metrics_descriptions)
    
    return header.format(metrics_descriptions=combined_descriptions)

def build_prompt_messages(modalities, with_metrics=False, with_fewshot=False, metrics_list=None):
    prompt_dict = load_all_prompts()

    messages = {}

    for key in modalities:
        if key not in prompt_dict["modality"]:
            raise ValueError(f"Unknown modality: {key}")
        msg = prompt_dict["modality"][key]
        if with_fewshot:
            msg += prompt_dict["fewshot"]
        messages[key] = SystemMessagePromptTemplate.from_template(msg).format_messages()

    if with_metrics:
        if metrics_list is not None:
            # Use dynamic metrics prompt based on selected metrics
            metrics_prompt = load_metrics_prompts(metrics_list)
        else:
            # Fallback to original fixed prompt
            metrics_prompt = prompt_dict["metrics"]
        
        messages["metrics"] = SystemMessagePromptTemplate.from_template(metrics_prompt).format_messages()

    messages["head"] = SystemMessagePromptTemplate.from_template(prompt_dict["head"]).format_messages()
    
    return messages

