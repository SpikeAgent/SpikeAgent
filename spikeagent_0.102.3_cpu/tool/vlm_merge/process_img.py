import io
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from PIL import Image
import math
import base64
from tqdm import tqdm

import spikeinterface.widgets as sw

def concat_images_horizontally(b64_images, resize_height=300):
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
    
    return new_img

def plot_encoded_img(encoded_img, title=""):
    img = Image.open(io.BytesIO(base64.b64decode(encoded_img)))
    plt.figure(figsize=(12, 4))
    plt.imshow(img)
    plt.title(title)
    plt.axis('off')
    plt.tight_layout()


def plot_merge_results(results_df, encoded_img_df):
    """
    Create a figure with spike waveform images and their scores, separated into Good and Noise classifications.
    Handles dynamic grid layout and removes empty subplots.

    Args:
        csv_file (str): Path to the CSV file containing spike classification results.
        waveform_plot_folder (str): Folder containing the spike waveform images.

    Returns:
        None: Displays the figure.
    """
    # Separate Good and Noise spikes
    for i, row in enumerate(results_df.itertuples()):
        fig, ax = plt.subplots(1, 1, figsize=(15, 4))
        group_id = row.Index
        merge_type = row.merge_type
        merge_units = row.merge_units
        img_base64 = encoded_img_df.loc[group_id]
        img = concat_images_horizontally(img_base64)
        ax.imshow(img)
        ax.axis("off")
        ax.set_title(f"Group ID: {group_id}(Unit {merge_units})\nMerge Decision: {merge_type}", fontsize=10)