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

    buffer = io.BytesIO()
    new_img.save(buffer, format="jpeg")
    merged_bytes = buffer.getvalue()
    new_img_base64 = base64.b64encode(merged_bytes).decode("utf-8")
    
    return new_img_base64

def plot_encoded_img(encoded_img, title=""):
    img = Image.open(io.BytesIO(base64.b64decode(encoded_img)))
    plt.figure(figsize=(12, 4))
    plt.imshow(img)
    plt.title(title)
    plt.axis('off')
    plt.tight_layout()


def plot_spike_images_with_result(results_df, encoded_img_df, feature="waveform_single"):
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
    good_spikes = results_df[results_df["final_classification"] == 'Good']
    bad_spikes = results_df[results_df["final_classification"] == 'Bad']

    def plot_class_spikes(spike_data, title, num_cols=5):
        num_spikes = len(spike_data)
        num_rows = math.ceil(num_spikes / num_cols)

        # Create a figure for this class
        fig, axes = plt.subplots(num_rows, num_cols, figsize=(15, 3 * num_rows))
        axes = axes.flatten()  # Flatten in case of multiple rows

        for i, row in enumerate(spike_data.itertuples()):
            unit_id = row.Index
            spike_score = row.average_score
            img_base64 = encoded_img_df.loc[unit_id, feature]
            img_binary = base64.b64decode(img_base64)
            img_buffer = io.BytesIO(img_binary)
            img = mpimg.imread(img_buffer, format="jpeg")
            axes[i].imshow(img)
            axes[i].axis("off")
            axes[i].set_title(f"Unit ID: {unit_id}\nScore: {spike_score:.2f}", fontsize=10)

        # Hide unused axes
        for j in range(i + 1, len(axes)):
            axes[j].axis("off")
        plt.tight_layout()
        fig.suptitle(title, fontsize=16, y=1.01)
        plt.show()

    # Plot Good spikes
    if len(good_spikes) > 0:
        plot_class_spikes(good_spikes, 'Good')
        
    if len(bad_spikes) > 0:
        plot_class_spikes(bad_spikes, 'Bad')