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

def run_vlm_curation(model, sorting_analyzer, img_df, features: list[str]=MODALITY, good_ids=[], bad_ids=[], with_metrics=False, metrics_list: list[str]=None, unit_ids=None,num_workers=50):
    unit_ids_ = list(sorting_analyzer.unit_ids) if unit_ids is None else unit_ids

    metrics = None
    if with_metrics:
        # Default metrics if none specified
        if metrics_list is None:
            metrics_list = ["snr", "isi_violations_ratio", "l_ratio"]
        
        metrics = sorting_analyzer.get_extension('quality_metrics').get_data()
        # Validate that requested metrics exist in the data
        available_metrics = metrics.columns.tolist()
        valid_metrics = [m for m in metrics_list if m in available_metrics]
        if not valid_metrics:
            raise ValueError(f"None of the requested metrics {metrics_list} are available. Available metrics: {available_metrics}")
        if len(valid_metrics) != len(metrics_list):
            missing_metrics = [m for m in metrics_list if m not in available_metrics]
            print(f"Warning: The following metrics are not available and will be skipped: {missing_metrics}")
        
        metrics = metrics[valid_metrics]
        metrics = metrics.loc[unit_ids_]
    
    encoded_img_df = img_df.loc[unit_ids_,features]

    with_fewshot = False if len(good_ids)+len(bad_ids) == 0 else True

    system_messages = build_prompt_messages(features, with_metrics, with_fewshot, metrics_list if with_metrics else None)

    results_df = async_run(
        model,
        encoded_img_df,
        features,
        system_messages,
        good_ids,
        bad_ids,
        metrics,
        num_workers=num_workers
    )

    return results_df





