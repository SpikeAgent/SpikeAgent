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

nest_asyncio.apply()

# Define the structured output for spike waveform classification
class SpikeClassification(BaseModel):
    """Structured output for spike classification."""
    merge_type: Literal["merge","not merge"]="Whether if pair of unit should be merged or not"
    reasoning: str = Field(description="Detailed reasoning for your decision.")

feature_caption_map = {
    "waveform_single": "Single-channel average waveform of candidate units",
    "waveform_multi": "Multi-channel template of candidate units",
    "spike_locations": "Spike location scatter plot of candidate units",
    "amplitude_plot": "Amplitude over time plot of candidate units",
    "crosscorrelograms": "Crosscorrelograms between candidate units",
    "pca_clustering": "PCA clustering analysis of candidate units"
}

def concat_images_horizontally(b64_images, resize_height=300):
    import io
    from PIL import Image
    import base64
    images = [Image.open(io.BytesIO(base64.b64decode(b64))) for b64 in b64_images]

    if resize_height is not None:
        images = [
            img.resize((int(img.width * resize_height / img.height), resize_height))
            for img in images
        ]
    
    total_width = sum(img.width for img in images)
    max_height = max(img.height for img in images)
    
    new_img = Image.new("RGB", (total_width, max_height), (255, 255, 255))
    
    x_offset = 0
    for img in images:
        new_img.paste(img, (x_offset, 0))
        x_offset += img.width

    buffer = io.BytesIO()
    new_img.save(buffer, format="jpeg")
    merged_bytes = buffer.getvalue()
    new_img_base64 = base64.b64encode(merged_bytes).decode("utf-8")
    
    return new_img_base64

def create_fewshot_messages(encoded_img_df, features, good_merge_groups, bad_merge_groups):
    fewshot_messages = {f:[] for f in features}
    if len(good_merge_groups) > 0:
        for f in features:
            content = [{"type": "text", "text": "These are Good merge examples you must compare with"}]
            for group_id in good_merge_groups:
                img = encoded_img_df.loc[group_id,f]
                content.append({"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img}"}})
            fewshot_messages[f].append(HumanMessage(content = content))
    if len(bad_merge_groups) > 0:
        for f in features:
            content = [{"type": "text", "text": "These are Bad merge examples you must compare with"}]
            for group_id in bad_merge_groups:
                img = encoded_img_df.loc[group_id,f]
                content.append({"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img}"}})
            fewshot_messages[f].append(HumanMessage(content = content))

    return fewshot_messages

async def process_feature(model, merge_unit_group, one_image, system_msg, fewshot_msg, feature):
    img_message = [HumanMessage(content=[
        {"type": "text", "text": f"Assess the quality of this {feature_caption_map[feature]} of unit list: {merge_unit_group}"},
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


# Asynchronous function to classify a spike waveform independently
async def process_unit(model, group_id, encoded_img, merge_unit_group, **kwargs):
    #await asyncio.sleep(1)
    system_messages = kwargs.get('system_messages')
    features = kwargs.get('features')
    fewshot_messages = kwargs.get('fewshot_messages')

    tasks = [process_feature(model, merge_unit_group, encoded_img[f], system_messages[f], fewshot_messages[f], f) for f in features]

    responses = await asyncio.gather(*tasks)
    final_input = ["These are the quality assessment report from Visual Language Model"]
    final_input += responses
    indent = "-"*50
    content = f"\n{indent}\n".join(final_input)
    report_msg = [HumanMessage(content = content)]
    structured_llm = model.with_structured_output(SpikeClassification)

    head_sys_msg = system_messages['head']

    img_message = [HumanMessage(content=[
        {"type": "text", "text": f"This is the feature image given of unit list: {merge_unit_group}"},
        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{concat_images_horizontally(encoded_img)}"}}
    ])]

    input_message = head_sys_msg+img_message+report_msg

    max_retries = 10
    attempt = 0

    while attempt < max_retries:
        try:
            response = await structured_llm.ainvoke(input_message)
            return {"group_id": group_id,
                     "merge_type": response.merge_type, 
                     "merge_units": merge_unit_group,
                     "reasoning": response.reasoning,
                     "report": content}
        
        except Exception as e:
            attempt += 1
            print(f"❌ Error processing group {group_id}, attempt {attempt}: {e}")
            if attempt == max_retries:
                print(f"🚫 Skipping group {group_id} after {max_retries} failures.")
                return {"group_id": group_id,
                        "merge_type": "", 
                        "merge_units": [],
                        "reasoning": "",
                        "report": ""}
            await asyncio.sleep(1)  # Optional delay between retries


async def run_in_batch(model, group_ids, encoded_img_df, num_workers, merge_unit_groups, **kwargs):
    results = []
    semaphore = asyncio.Semaphore(num_workers)
    len_feature = len(kwargs.get('features',[0]))
    batch_size = num_workers//(3*len_feature)
        
    async def limited_task(group_id, progress_bar):
        async with semaphore:
            encoded_img = encoded_img_df.loc[group_id]
            merge_unit_group = merge_unit_groups[group_id]
            result = await process_unit(model, group_id, encoded_img, merge_unit_group,**kwargs)
            progress_bar.update(1) 
            return result

    with tqdm(total=len(encoded_img_df), desc="Processing Groups", unit="unit", file=sys.stdout, leave=True) as progress_bar:
        tasks = [limited_task(group_id, progress_bar) for group_id in group_ids]
        for i in range(0, len(tasks), batch_size):
            batch = tasks[i:i + batch_size]
            results.extend(await asyncio.gather(*batch))
            
    return results

def async_run(
    model,
    merge_unit_groups,
    encoded_img_df,
    features,
    system_messages,
    good_merge_groups=[],
    bad_merge_groups=[],
    num_workers=50
    ):
    fewshot_messages = create_fewshot_messages(encoded_img_df, features, good_merge_groups, bad_merge_groups)
    
    group_ids = encoded_img_df.index.tolist()

    results = asyncio.run(run_in_batch(
        model=model, 
        group_ids = group_ids,
        encoded_img_df=encoded_img_df, 
        num_workers=num_workers, 
        merge_unit_groups=merge_unit_groups,
        features=features,
        system_messages=system_messages,
        fewshot_messages=fewshot_messages,
    ))
    results_df = pd.DataFrame(results)
    results_df = results_df.sort_values(by="group_id", ascending=True)
    results_df.set_index("group_id", inplace=True)

    return results_df



