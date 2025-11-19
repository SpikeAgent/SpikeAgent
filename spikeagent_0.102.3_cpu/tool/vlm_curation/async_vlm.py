import os
import asyncio
import pandas as pd
from langchain_core.messages import HumanMessage
from pydantic import BaseModel, Field
from typing import Literal
from statistics import mean
from collections import Counter
import nest_asyncio
from tqdm.asyncio import tqdm
import sys
# Import and load environment variables

from .process_img import concat_images_horizontally, plot_encoded_img

nest_asyncio.apply()

# Define the structured output for spike waveform classification
class UnitCuration(BaseModel):
    """Structured output for spike classification."""

    reasoning: str = Field(description="Detailed explanation combining insights from each modality.")
    unit_quality_score: float = Field(description="Quality score between 0.0 (bad) and 1.0 (excellent).")
    classification: Literal["Good", "Bad", "Error"] = Field(description="Final label. Use 'Error' only if something went wrong.")

featrue_caption_map = {
    "waveform_single": "Single-channel average waveform",
    "waveform_multi": "Multi-channel average waveform (template)",
    "autocorr": "Autocorrelogram of spike times",
    "spike_locations": "Spike location scatter plot",
    "amplitude_plot": "Amplitude over time plot",
}

def create_fewshot_messages(encoded_img_df, features, good_ids, bad_ids):
    fewshot_messages = {f:[] for f in features}
    if len(good_ids) > 0:
        for f in features:
            content = [{"type": "text", "text": "These are Good examples you must compare with"}]
            for id in good_ids:
                img = encoded_img_df.loc[id,f]
                content.append({"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img}"}})
            fewshot_messages[f].append(HumanMessage(content = content))
    if len(bad_ids) > 0:
        for f in features:
            content = [{"type": "text", "text": "These are Bad examples you must compare with"}]
            for id in bad_ids:
                img = encoded_img_df.loc[id,f]
                content.append({"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img}"}})
            fewshot_messages[f].append(HumanMessage(content = content))

    return fewshot_messages


async def process_feature(model, one_image, system_msg, fewshot_msg):
    img_message = [HumanMessage(content=[
        {"type": "text", "text": f"Assess the quality of this feature image"},
        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{one_image}"}}
    ])]
    input_message = system_msg + fewshot_msg + img_message

    max_retries = 10
    attempt = 0

    while attempt < max_retries:
        try:
            response = await model.ainvoke(input_message)
            return response.content
        
        except Exception as e:
            attempt += 1
            print(f"❌ Error processing unit, attempt {attempt}: {e}")
            if attempt == max_retries:
                print(f"🚫 Skipping after {max_retries} failures.")
                return ""
            await asyncio.sleep(1)  # Optional delay between retries

async def process_metrics(model, metrics, unit_id, system_msg):
    qm = metrics.loc[unit_id]
    metrics_msg = [HumanMessage(content=[{"type": "text", "text": "These are the quality metrics of this unit. Assess the quality. - "+
                        ",".join(f"{k}: {v:.5f}" for k, v in qm.items())}])]
    input_message = system_msg + metrics_msg

    max_retries = 10
    attempt = 0

    while attempt < max_retries:
        try:
            response = await model.ainvoke(input_message)
            return response.content
        
        except Exception as e:
            attempt += 1
            print(f"❌ Error processing unit, attempt {attempt}: {e}")
            if attempt == max_retries:
                print(f"🚫 Skipping after {max_retries} failures.")
                return ""
            await asyncio.sleep(1)  # Optional delay between retries




# Asynchronous function to classify a spike waveform independently
async def process_unit(model, unit_id, encoded_images, reviewer_id, **kwargs):
    #await asyncio.sleep(1)
    fewshot_messages = kwargs.get('fewshot_messages')
    features = kwargs.get('features')
    metrics = kwargs.get('metrics')
    system_messages = kwargs.get('system_messages')

    tasks = [process_feature(model, encoded_images[f], system_messages[f], fewshot_messages[f]) for f in features]
    
    if metrics is not None:
        system_msg = system_messages['metrics']
        tasks.append(process_metrics(model, metrics, unit_id, system_msg))

    responses = await asyncio.gather(*tasks)
    final_input = ["These are the quality assessment report from Visual Language Model\n" + "-"*50]
    final_input += responses

    content = "\n".join(final_input)
    report_msg = [HumanMessage(content = content)]
    structured_llm = model.with_structured_output(UnitCuration)

    head_sys_msg = system_messages['head']
    input_msg = head_sys_msg+report_msg

    max_retries = 10
    attempt = 0

    while attempt < max_retries:
        try:
            response = await structured_llm.ainvoke(input_msg)
            return {"reviewer_id": reviewer_id, "response": response}
        
        except Exception as e:
            attempt += 1
            print(f"❌ Error processing unit, attempt {attempt}: {e}")
            if attempt == max_retries:
                print(f"🚫 Skipping after {max_retries} failures.")
                return {"reviewer_id": reviewer_id, "response": UnitCuration(
                    classification="Error",
                    unit_quality_score=0,
                    reasoning=''
                )}
            await asyncio.sleep(1)  # Optional delay between retries
    

# Function to aggregate results from all reviewers
def aggregate_results(reviews, unit_id):
    unit_quality_scores = [r["response"].unit_quality_score for r in reviews]
    classifications = [r["response"].classification for r in reviews]

    # Average spike score
    average_score = round(mean(unit_quality_scores), 2)

    # Majority vote for classification
    good_count = Counter(classifications)["Good"]
    if good_count > 1:
        majority_classification = "Good"
    else:
        majority_classification = "Bad"

    # Combine reasoning for transparency
    combined_reasoning = "\n".join([f"Reviewer {r['reviewer_id']}: {r['response'].reasoning}" for r in reviews])

    # Extract individual results
    individual_scores = {f"reviewer_{r['reviewer_id']}_score": r["response"].unit_quality_score for r in reviews}
    individual_classes = {f"reviewer_{r['reviewer_id']}_class": r["response"].classification for r in reviews}

    return {
        "unit_ids": unit_id,
        "average_score": average_score,
        "final_classification": majority_classification,
        "combined_reasoning": combined_reasoning,
        **individual_scores,
        **individual_classes
    }
    
# Asynchronous function to process a single unit_id with ensemble reviewers
async def async_run_with_reviewers(model, unit_id, encoded_images, **kwargs):
    #await asyncio.sleep(1)
    reviewers = [1, 2, 3]
    tasks = [process_unit(model, unit_id, encoded_images, reviewer_id, **kwargs) for reviewer_id in reviewers]
    reviews = await asyncio.gather(*tasks)

    # Aggregate results
    aggregated_result = aggregate_results(reviews, unit_id)
    return aggregated_result

async def run_in_batch(model, unit_ids, encoded_img_df, num_workers, **kwargs):
    results = []
    semaphore = asyncio.Semaphore(num_workers)
    len_feature = len(kwargs.get('features',[0]))
    batch_size = num_workers//(3*len_feature)
        
    async def limited_task(unit_id, progress_bar):
        async with semaphore:
            encoded_images = encoded_img_df.loc[unit_id]
            result = await async_run_with_reviewers(model, unit_id, encoded_images, **kwargs)
            progress_bar.update(1) 
            return result

    with tqdm(total=len(encoded_img_df), desc="Processing Units", unit="unit", file=sys.stdout, leave=True) as progress_bar:
        tasks = [limited_task(unit_id, progress_bar) for unit_id in unit_ids]
        for i in range(0, len(tasks), batch_size):
            batch = tasks[i:i + batch_size]
            results.extend(await asyncio.gather(*batch))
            
    return results

def async_run(
    model,
    encoded_img_df,
    features,
    system_messages,
    good_ids=[],
    bad_ids=[],
    metrics:pd.DataFrame|None=None,
    num_workers=50
):
    if metrics is not None:
        assert (len(encoded_img_df) == len(metrics))
    fewshot_messages = create_fewshot_messages(encoded_img_df, features, good_ids, bad_ids)

    unit_ids = encoded_img_df.index.tolist()

    results = asyncio.run(run_in_batch(
        model=model, 
        unit_ids = unit_ids,
        encoded_img_df=encoded_img_df, 
        num_workers=num_workers, 
        features=features,
        system_messages=system_messages, 
        fewshot_messages=fewshot_messages, 
        metrics=metrics
    ))
    results_df = pd.DataFrame(results)
    results_df = results_df.sort_values(by="unit_ids", ascending=True)
    results_df.set_index("unit_ids", inplace=True)

    return results_df



