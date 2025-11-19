import math
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import gridspec
import spikeinterface.widgets as sw
from tqdm import tqdm
import matplotlib.image as mpimg
from PIL import Image
import io
import math
import base64
import pandas as pd
import os

FEATURES = ["waveform_single","waveform_multi","autocorr","spike_locations","amplitude_plot"]

def create_img_df(
    sorting_analyzer, 
    features=FEATURES, 
    unit_ids=None, 
    load_if_exists=True,
    **kwargs
):  
    save_path = os.path.join(os.path.dirname(sorting_analyzer.folder), 'encoded_img.csv')
    if os.path.exists(save_path):
        if load_if_exists:
            df = pd.read_csv(save_path, index_col='unit_id')
            return df
        else:
            os.remove(save_path)
    
    dpi = kwargs.get('dpi', 300)
    num_channels = kwargs.get('num_channels', 6)
    unit_ids_ = sorting_analyzer.unit_ids if unit_ids is None else unit_ids
    unit_locations = sorting_analyzer.get_extension('unit_locations').get_data()
    sparsity = sorting_analyzer.sparsity
    sparsity_1 = sparsity.from_best_channels(sorting_analyzer, num_channels=1)
    sparsity_n = sparsity.from_best_channels(sorting_analyzer, num_channels=num_channels)
    

    def waveform_single(unit_id, ax):
        color = kwargs.get('w_color', 'black')
        sw.plot_unit_templates(
                    sorting_analyzer, 
                    unit_ids=[unit_id],
                    axes=[ax],
                    sparsity=sparsity_1,
                    plot_legend=False,
                    unit_colors={unit_id:color}
                )
        ax.set_title("Single-channel Waveform")

    def waveform_multi(unit_id, ax):
        color = kwargs.get('w_color', 'black')
        sw.plot_unit_templates(
                    sorting_analyzer, 
                    unit_ids=[unit_id],
                    axes=[ax],
                    sparsity=sparsity_n,
                    plot_legend=False,
                    unit_colors={unit_id:color}
                )
        ax.set_title("Multi-channel Waveform")

    def autocorr(unit_id, ax):
        sw.plot_autocorrelograms(
            sorting_analyzer,
            unit_ids=[unit_id],
            ax=ax
        )
        ax.set_title("Autocorrelogram")

    def spike_locations(unit_id, ax):
        idx = np.where(sorting_analyzer.unit_ids==unit_id)[0][0]
        x, y, _ = unit_locations[idx]
        margin = kwargs.get("margin", 40)
        with_channel_ids = kwargs.get('with_channel_ids', True)
        color = kwargs.get('loc_color', 'green')
        ch_font =  kwargs.get('ch_font', 6)
        sw.plot_spike_locations(
            sorting_analyzer,
            unit_ids=[unit_id],
            ax=ax,
            plot_legend=False,
            with_channel_ids=with_channel_ids,
            unit_colors={unit_id:color}
        )
        for text in ax.texts:
            text.set_fontsize(ch_font)

        ax.set_xlim(x - margin, x + margin)
        ax.set_ylim(y - margin, y + margin)
        ax.set_title("Spike locations")

    def amplitude_plot(unit_id, ax):
        color = kwargs.get('a_color', 'black')
        sw.plot_amplitudes(
            sorting_analyzer, 
            unit_ids=[unit_id],
            ax=ax,
            plot_legend=False,
            unit_colors={unit_id:color}
        )
        ax.set_title("Amplitude")

    feature_map = {
        "waveform_single": {"func": waveform_single, "fig_size": (3,3)},
        "waveform_multi": {"func": waveform_multi, "fig_size": (3,3)},
        "autocorr": {"func": autocorr, "fig_size": (4,3)},
        "spike_locations": {"func": spike_locations, "fig_size": (3,3)},
        "amplitude_plot": {"func": amplitude_plot, "fig_size": (10,3)},
    }

    img_array = []
    print(f'Encoding {len(unit_ids_)} unit images..')
    for unit_id in tqdm(unit_ids_):
        encoded_images = []
        for f in features:
            plot_func = feature_map[f]["func"]
            figsize = feature_map[f]["fig_size"]
            fig, ax = plt.subplots(1, 1, figsize=figsize)
            plot_func(unit_id, ax)
            img_buffer = io.BytesIO()
            plt.savefig(img_buffer, format="jpeg", dpi=dpi, bbox_inches='tight', transparent=True)
            plt.close(fig)
            img_buffer.seek(0)
            encoded_img = base64.b64encode(img_buffer.getvalue()).decode('utf-8')
            encoded_images.append(encoded_img)
        img_array.append(encoded_images)
    
    df = pd.DataFrame(img_array, columns=features)
    df.index = unit_ids_
    df.index.name = "unit_id"
    df.to_csv(save_path)

    return df


def concat_images_horizontally(b64_images, resize_height=None):
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

def plot_units_with_features_df(
    sorting_analyzer,
    encoded_img_df, 
    features=FEATURES, 
    unit_ids = None,
    save = False,
    resize_height=300
):
    for f in features:
        if f not in encoded_img_df.columns:
            raise ValueError(f'{f} not in img_df\nAvailable inputs: {FEATURES}')
    if save:
        save_folder = os.path.join(sorting_analyzer.folder,'feature_plot')
        os.makedirs(save_folder, exist_ok=True)

    unit_ids_ = sorting_analyzer.unit_ids if unit_ids is None else unit_ids

    for unit_id in unit_ids_:
        concatenated_img = concat_images_horizontally(encoded_img_df.loc[unit_id,features], resize_height)
        plt.figure(figsize=(12, 4))
        plt.imshow(concatenated_img)
        plt.title(f'Unit {unit_id}')
        plt.axis('off')
        plt.tight_layout()
        if save:
            plt.savefig(os.path.join(save_folder,f'unit_{unit_id}'))
            

def plot_unit_templates(sorting_analyzer, unit_ids=None, num_channels=1, ncols=8, color=None):
    unit_ids_ = unit_ids if unit_ids is not None else sorting_analyzer.unit_ids
    num_unit = len(unit_ids_)

    sparsity = sorting_analyzer.sparsity
    sparsity = sparsity.from_best_channels(sorting_analyzer, num_channels=num_channels)

    unit_colors = None
    if color is not None:
        unit_colors = {unit_id: color for unit_id in unit_ids_}

    nrows = math.ceil(num_unit / ncols)
    figsize = (ncols * 3, nrows * 3)

    fig, axes = plt.subplots(nrows, ncols, figsize=figsize)
    axes = axes.flatten()

    sw.plot_unit_templates(
        sorting_analyzer,
        unit_ids=unit_ids_,    
        sparsity=sparsity,
        axes=axes[:num_unit],
        unit_colors=unit_colors
    )

    for i, ax in enumerate(axes):
        ax.set_xticks([])
        if i >= num_unit:
            ax.remove()

    plt.tight_layout()


def plot_autocorrelograms(sorting_analyzer, unit_ids=None, ncols=8):
    unit_ids_ = unit_ids if unit_ids is not None else sorting_analyzer.unit_ids
    num_unit = len(unit_ids_)

    nrows = math.ceil(num_unit / ncols)
    figsize = (ncols * 4, nrows * 3)

    fig, axes = plt.subplots(nrows, ncols, figsize=figsize)
    axes = axes.flatten()

    sw.plot_autocorrelograms(
        sorting_analyzer,
        unit_ids=unit_ids_,
        axes=axes[:num_unit]
    )

    for i, ax in enumerate(axes):
        ax.set_yticks([])
        if i >= num_unit:
            ax.remove()

    plt.tight_layout()


def plot_spike_locations(sorting_analyzer, unit_ids=None, margin=20, ncols=4, color=None):
    """
    Rasterized spike location plots for selected units with zoomed-in view.

    Parameters:
        sorting_analyzer: SpikeInterface SortingAnalyzer
        unit_ids: list of unit ids to plot (default: all)
        margin: zoom margin (default: 20)
        ncols: number of columns in subplot grid (default: 4)
    """
    unit_ids_ = unit_ids if unit_ids is not None else sorting_analyzer.unit_ids
    num_unit = len(unit_ids_)

    unit_colors = None
    if color is not None:
        unit_colors = {unit_id: color for unit_id in unit_ids_}
    
    nrows = math.ceil(num_unit / ncols)
    figsize = (ncols * 4, nrows * 4)
    fig, axes = plt.subplots(nrows, ncols, figsize=figsize)
    axes = axes.flatten()

    unit_locations = sorting_analyzer.get_extension('unit_locations').get_data()

    for i, unit_id in enumerate(unit_ids_):
        idx = np.where(sorting_analyzer.unit_ids==unit_id)[0][0]
        ax = axes[i]
        x, y, _ = unit_locations[idx]
        
        sw.plot_spike_locations(
            sorting_analyzer,
            unit_ids=[unit_id],
            ax=ax,
            with_channel_ids=True,
            unit_colors=unit_colors
        )
        ax.set_xlim(x - margin, x + margin)
        ax.set_ylim(y - margin, y + margin)
        ax.set_title(f"Unit {unit_id}")
        ax.set_xticks([])
        ax.set_yticks([])

    for j in range(num_unit, len(axes)):
        axes[j].remove()

    plt.tight_layout()



def plot_rasters(sorting_analyzer, unit_ids=None, time_range = (0,100)):
    time_range_ = time_range
    if time_range is None:
        end = sorting_analyzer.get_total_duration()
        time_range_ = (0,end)
    unit_ids_ = unit_ids if unit_ids is not None else sorting_analyzer.unit_ids
    num_unit = len(unit_ids_)

    height_per_unit = 0.35
    max_height = 20
    fig_height = min(4 + num_unit * height_per_unit, max_height)
    figsize = (10, fig_height)

    fig, ax = plt.subplots(figsize=figsize)

    sw.plot_rasters(
        sorting=sorting_analyzer,
        unit_ids=unit_ids_,
        ax=ax,
        color="black",
        time_range = time_range_
    )

    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Unit")

    plt.tight_layout()


def plot_units_with_features(sorting_analyzer, features=["waveform_single","waveform_multi","autocorr","spike_locations","amplitude_plot"], unit_ids=None,**kwargs):
    unit_ids_ = sorting_analyzer.unit_ids if unit_ids is None else unit_ids
    unit_locations = sorting_analyzer.get_extension('unit_locations').get_data()
    sparsity = sorting_analyzer.sparsity
    sparsity_1 = sparsity.from_best_channels(sorting_analyzer, num_channels=1)
    num_channels = kwargs.get('num_channels', 6)
    sparsity_6 = sparsity.from_best_channels(sorting_analyzer, num_channels=num_channels)

    def waveform_single(unit_id, ax):
        sw.plot_unit_templates(
                    sorting_analyzer, 
                    unit_ids=[unit_id],
                    axes=[ax],
                    sparsity=sparsity_1,
                    plot_legend=False,
                    unit_colors={unit_id:'black'}
                )
        ax.set_title("Single-channel Waveform")
        ax.set_xticks([])
    def waveform_multi(unit_id, ax):
        sw.plot_unit_templates(
                    sorting_analyzer, 
                    unit_ids=[unit_id],
                    axes=[ax],
                    sparsity=sparsity_6,
                    plot_legend=False,
                    unit_colors={unit_id:'black'}
                )
        ax.set_title("Multi-channel Waveform")
        ax.set_xticks([])
    def autocorr(unit_id, ax):
        sw.plot_autocorrelograms(
            sorting_analyzer,
            unit_ids=[unit_id],
            ax=ax
        )
        ax.set_title("Autocorrelogram")
    def spike_locations(unit_id, ax):
        margin = kwargs.get('margin', 40)
        with_channel_ids = kwargs.get('with_channel_ids', True)
        idx = np.where(sorting_analyzer.unit_ids==unit_id)[0][0]
        x, y, _ = unit_locations[idx]
        sw.plot_spike_locations(
            sorting_analyzer,
            unit_ids=[unit_id],
            ax=ax,
            plot_legend=False,
            with_channel_ids=with_channel_ids,
            unit_colors={unit_id:'green'}
        )
        ax.set_xlim(x - margin, x + margin)
        ax.set_ylim(y - margin, y + margin)
        #ax.set_xticks([])
        #ax.set_yticks([])
        ax.set_title("Spike locations")
    def amplitude_plot(unit_id, ax):
        sw.plot_amplitudes(
            sorting_analyzer, 
            unit_ids=[unit_id],
            ax=ax,
            plot_legend=False,
            unit_colors={unit_id:'black'}
        )
        ax.set_title("Amplitude")

    modality_func_map = {
        "waveform_single": waveform_single,
        "waveform_multi": waveform_multi,
        "autocorr": autocorr,
        "spike_locations": spike_locations,
        "amplitude_plot": amplitude_plot,
    }

    n_modality = len(features)
    figsize = (3*n_modality, 3)
    for unit_id in unit_ids_:
        fig, axes = plt.subplots(1,n_modality, figsize=figsize)
        fig.suptitle(f'Unit {unit_id}')
        if n_modality == 1:
            axes = [axes]
        for modality,ax in zip(features, axes):
            plot_func = modality_func_map[modality]
            plot_func(unit_id, ax)
            legend = ax.get_legend()
            if legend is not None:
                legend.remove()

        plt.legend().remove()
        plt.tight_layout()


def plot_metrics_summary(sorting_analyzer, max_isi=1.5, min_snr=5.0):
    """
    Generate summary figure showing quality metrics and spike time locations.
    """
    metrics = sorting_analyzer.get_extension('quality_metrics').get_data()
    
    fig = plt.figure(figsize=(10, 10))
    grid = gridspec.GridSpec(3, 3, figure=fig, hspace=0.5, wspace=0.5)

    ax = fig.add_subplot(grid[0, 0:])
    sw.plot_rasters(
        sorting_analyzer=sorting_analyzer,
        ax=ax,color="black",
        time_range = (0,100),\
    )
    ax.set_xlim(0, 10)
    ax.set_yticks([])
    #ax.set_ylim(0, len(sorting_analyzer.channel_ids))
    ax.set_xlabel('Time (s)')
    ax.set_ylabel('Channels')
    ax.set_title('Spikes from Channels')

    firing_rate = metrics['firing_rate']
    firing_rate[firing_rate > 20] = firing_rate
    ax = fig.add_subplot(grid[1, 0])
    ax.hist(firing_rate, bins=50, color='grey')
    ax.set_xlabel('firing rate (Hz)')
    ax.set_ylabel('# of units')
    #ax.set_xlim(0,20)

    snr = metrics['snr']
    snr[snr > 20] = 20
    ax = fig.add_subplot(grid[1, 1])
    ax.hist(snr, bins=50, color='grey')
    ax.axvline(min_snr, color='black', linestyle='--')
    ax.set_title(f'> {min_snr} = good units')
    ax.set_xlabel('snr')
    ax.set_ylabel('# of units')
    #ax.set_xlim(0,20)

    isi = metrics['isi_violations_ratio']
    isi[isi > 20] = 20
    ax = fig.add_subplot(grid[1, 2])
    ax.hist(isi, bins=100, color='grey')
    ax.axvline(max_isi, color='black', linestyle='--')
    ax.set_title(f'< {max_isi} = good units')
    ax.set_xlabel('isi violations ratio')
    ax.set_ylabel('# of units')
    #ax.set_xlim(0,20)

    ax = fig.add_subplot(grid[2, 0])
    ax.hist(metrics['amplitude_median'], bins=50, color='grey')
    ax.set_xlabel('amplitude median')
    ax.set_ylabel('# of units')


    ax = fig.add_subplot(grid[2, 1])
    ax.hist(metrics['l_ratio'], bins=50, color='grey')
    ax.set_xlabel('L-ratio')
    ax.set_ylabel('# of units')

    good_i = metrics.loc[metrics['isi_violations_ratio'] < max_isi, 'firing_rate']
    good_a = metrics.loc[metrics['isi_violations_ratio'] < max_isi, 'amplitude_median']
    bad_i = metrics.loc[metrics['isi_violations_ratio'] >= max_isi, 'firing_rate']
    bad_a = metrics.loc[metrics['isi_violations_ratio'] >= max_isi, 'amplitude_median']

    ax = fig.add_subplot(grid[2, 2])
    ax.scatter(good_i, good_a, color='blue', alpha=0.5, label='good', s=5)
    ax.scatter(bad_i, bad_a, color='red', alpha=0.5, label='bad', s=5)
    ax.set_xlabel('firing rate (Hz)')
    ax.set_ylabel('amplitude')
    ax.legend(loc='lower right')
