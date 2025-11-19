from .prompt_loader import build_prompt_messages
from .async_vlm import async_run

MODALITY = ["waveform_single","waveform_multi","autocorr","spike_locations","amplitude_plot"]

from langchain_core.messages import BaseMessage

def pretty_print_messages(messages: list[BaseMessage]):
    for i, msg in enumerate(messages):
        print(f"\n[{i+1}] {msg.type.upper()} MESSAGE")
        if hasattr(msg, "content"):
            print(msg.content)
        else:
            print("(No content)")

def run_vlm_curation(model, sorting_analyzer, img_df, features: list[str], good_ids=[], bad_ids=[], with_metrics=False, unit_ids=None,num_workers=50):
    unit_ids_ = list(sorting_analyzer.unit_ids) if unit_ids is None else unit_ids

    metrics = None
    if with_metrics:
        metrics = sorting_analyzer.get_extension('quality_metrics').get_data()
        metrics = metrics[["snr", "isi_violations_ratio", "presence_ratio", "amplitude_cutoff"]]
        metrics = metrics.loc[unit_ids_]
    
    encoded_img_df = img_df.loc[unit_ids_,features]

    with_fewshot = False if len(good_ids)+len(bad_ids) == 0 else True

    system_messages = build_prompt_messages(features, with_metrics, with_fewshot)

    results_df = async_run(
        model,
        encoded_img_df,
        system_messages,
        good_ids,
        bad_ids,
        metrics,
        num_workers=num_workers
    )

    return results_df




