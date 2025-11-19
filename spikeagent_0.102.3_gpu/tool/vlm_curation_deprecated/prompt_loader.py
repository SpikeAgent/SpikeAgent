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
        "head": SystemMessagePromptTemplate.from_template(load_prompt(f"{base_path}/head.txt")),
        "modality": {
            "waveform_single": SystemMessagePromptTemplate.from_template(load_prompt(f"{modality_path}/waveform_single.txt")),
            "waveform_multi": SystemMessagePromptTemplate.from_template(load_prompt(f"{modality_path}/waveform_multi.txt")),
            "autocorr": SystemMessagePromptTemplate.from_template(load_prompt(f"{modality_path}/autocorr.txt")),
            "spike_locations": SystemMessagePromptTemplate.from_template(load_prompt(f"{modality_path}/spike_locations.txt")),
            "amplitude_plot": SystemMessagePromptTemplate.from_template(load_prompt(f"{modality_path}/amplitude_plot.txt")),
        },
        "metrics": SystemMessagePromptTemplate.from_template(load_prompt(f"{base_path}/metrics.txt")),
        "fewshot": SystemMessagePromptTemplate.from_template(load_prompt(f"{base_path}/fewshot_instruction.txt")),
        "instruction": SystemMessagePromptTemplate.from_template(load_prompt(f"{base_path}/instruction.txt"))
    }

def build_prompt_messages(modalities, with_metrics=False, with_fewshot=False):
    prompt_dict = load_all_prompts()

    messages = []

    # format system message
    messages += prompt_dict["head"].format_messages()

    # format each modality block
    for key in modalities:
        if key not in prompt_dict["modality"]:
            raise ValueError(f"Unknown modality: {key}")
        messages += prompt_dict["modality"][key].format_messages()

    if with_metrics:
        messages += prompt_dict["metrics"].format_messages()

    if with_fewshot:
        messages += prompt_dict["fewshot"].format_messages()

    messages += prompt_dict["instruction"].format_messages()

    return messages

