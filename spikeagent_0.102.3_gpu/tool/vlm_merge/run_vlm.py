from .prompt_loader import build_prompt_messages
from .async_vlm import async_run

MODALITY = ["waveform_single","waveform_multi","crosscorrelograms","spike_locations","amplitude_plot","pca_clustering"]

from langchain_core.messages import BaseMessage

def pretty_print_messages(messages: list[BaseMessage]):
    for i, msg in enumerate(messages):
        print(f"\n[{i+1}] {msg.type.upper()} MESSAGE")
        if hasattr(msg, "content"):
            print(msg.content)
        else:
            print("(No content)")

def run_vlm_merge(model, merge_unit_groups, img_df, features: list[str]=MODALITY, good_merge_groups=[], bad_merge_groups=[], num_workers=50):
    

    with_fewshot = False if len(good_merge_groups)+len(bad_merge_groups) == 0 else True

    system_messages = build_prompt_messages(features, with_fewshot)

    results_df = async_run(
        model,
        merge_unit_groups,
        img_df,
        features,
        system_messages,
        good_merge_groups,
        bad_merge_groups,
        num_workers=num_workers
    )

    return results_df





