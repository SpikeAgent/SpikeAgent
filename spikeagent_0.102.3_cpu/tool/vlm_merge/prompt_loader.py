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
            "crosscorrelograms": load_prompt(f"{modality_path}/crosscorrelograms.txt"),
            "spike_locations": load_prompt(f"{modality_path}/spike_locations.txt"),
            "amplitude_plot": load_prompt(f"{modality_path}/amplitude_plot.txt"),
            "pca_clustering": load_prompt(f"{modality_path}/pca_clustering.txt"),
        },
        "fewshot": load_prompt(f"{base_path}/fewshot_instruction.txt"),
    }

def build_prompt_messages(modalities, with_fewshot=False):
    prompt_dict = load_all_prompts()

    messages = {}

    for key in modalities:
        if key not in prompt_dict["modality"]:
            raise ValueError(f"Unknown modality: {key}")
        msg = prompt_dict["modality"][key]
        if with_fewshot:
            msg += "\n\n" + prompt_dict["fewshot"]
        messages[key] = SystemMessagePromptTemplate.from_template(msg).format_messages()

    messages["head"] = SystemMessagePromptTemplate.from_template(prompt_dict["head"]).format_messages()
    
    return messages


