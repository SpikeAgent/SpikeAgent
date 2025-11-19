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
from spikeinterface.core import ChannelSparsity, get_template_extremum_channel

UNIT_FEATURES = ["waveform_single","waveform_multi","autocorr", "spike_locations","amplitude_plot"]
MERGE_FEATURES = ["waveform_single", "amplitude_plot","crosscorrelograms"]
default_colors = plt.get_cmap('tab10').colors

def create_unit_img_df(
    sortinganalyzer, 
    unit_ids=None, 
    features=UNIT_FEATURES,
    load_if_exists=True, 
    **kwargs
):
    save_path = os.path.join(os.path.dirname(sortinganalyzer.folder), 'unit_img.csv')
    if os.path.exists(save_path):
        if load_if_exists:
            df = pd.read_csv(save_path, index_col='unit_id')
            return df
        else:
            os.remove(save_path)

    unit_ids_ = sortinganalyzer.unit_ids if unit_ids is None else unit_ids

    img_array = []
    print(f'Encoding {len(unit_ids_)} unit images..')
    for unit_id in tqdm(unit_ids_):
        encoded_images = []
        feature_map = {
            "waveform_single": {"func": plot_waveform, "args": {"sortinganalyzer": sortinganalyzer, "unit_ids":[unit_id], "unit_colors":{unit_id: 'black'}, "alpha":1,"legend":False, "title":"Waveform single", "figsize":(5, 5), "peak_sign":'neg'}},
            "waveform_multi": {"func": plot_templates, "args" : {"sortinganalyzer": sortinganalyzer, "unit_ids":[unit_id], "unit_colors":{unit_id: 'black'}, "alpha":1,"legend":False, "title":"Waveform multi", "figsize":(5, 5), "num_channels":6}},
            "spike_locations": {"func": plot_spike_locations, "args":{"sortinganalyzer": sortinganalyzer, "unit_ids":[unit_id], "unit_colors":{unit_id: 'green'},"legend":False, "title":" Spike locations", "figsize":(5, 5), "margin":50, "with_channel_ids":False}},
            "amplitude_plot": {"func": plot_amplitude, "args":{"sortinganalyzer": sortinganalyzer, "unit_ids":[unit_id], "unit_colors":{unit_id: 'black'},"legend":False, "title":" Spike amplitude", "figsize":(15, 5), "y_lim":None}},
            "autocorr": {"func": plot_autocorrelogram,  "args":{"sortinganalyzer": sortinganalyzer, "unit_id":unit_id, "color":"green", "figsize":(5, 5)}},
        }
        for f in features:
            plot_func = feature_map[f]["func"]
            args = feature_map[f]["args"]
            plot_func(**args)
            img_buffer = io.BytesIO()
            plt.savefig(img_buffer, format="png", dpi=600, bbox_inches='tight', transparent=False)
            plt.close()
            img_buffer.seek(0)
            encoded_img = base64.b64encode(img_buffer.getvalue()).decode('utf-8')
            encoded_images.append(encoded_img)
        img_array.append(encoded_images)
    df = pd.DataFrame(img_array, columns=features)
    df.index = unit_ids_
    df.index.name = "unit_id"
    df.to_csv(save_path)
    return df

def create_merge_img_df(
    sortinganalyzer, 
    unit_groups, 
    features=MERGE_FEATURES,
    load_if_exists=True,
    **kwargs
):
    save_path = os.path.join(os.path.dirname(sortinganalyzer.folder), 'merge_img.csv')
    if os.path.exists(save_path):
        if load_if_exists:
            df = pd.read_csv(save_path, index_col='group_id')
            return df
        else:
            os.remove(save_path)

    img_array =[]
    for unit_group in tqdm(unit_groups):
        encoded_images = []
        unit_colors = dict(zip(unit_group, default_colors[:len(unit_group)]))
        feature_map = {
            "waveform_single": {"func": plot_waveform, "args": {"sortinganalyzer": sortinganalyzer, "unit_ids":unit_group, "unit_colors":unit_colors, "alpha":0.5,"legend":True, "title":"Waveform single", "figsize":(5, 5), "peak_sign":'neg'}},
            "waveform_multi": {"func": plot_templates, "args" : {"sortinganalyzer": sortinganalyzer, "unit_ids":unit_group, "unit_colors":unit_colors, "alpha":0.5,"legend":True, "title":"Waveform multi", "figsize":(5, 5), "num_channels":4}},
            "spike_locations": {"func": plot_spike_locations, "args":{"sortinganalyzer": sortinganalyzer, "unit_ids":unit_group, "unit_colors":unit_colors,"legend":True, "title":" Spike locations", "figsize":(5, 5), "margin":50, "with_channel_ids":False}},
            "amplitude_plot": {"func": plot_amplitude, "args":{"sortinganalyzer": sortinganalyzer, "unit_ids":unit_group, "unit_colors":unit_colors,"legend":True, "title":" Spike amplitude", "figsize":(10, 5), "y_lim":None, "plot_histograms":True}},
            "crosscorrelograms": {"func": plot_crosscorrelograms,  "args":{"sortinganalyzer": sortinganalyzer, "unit_ids":unit_group, "title":"Crosscorrelograms"}},
        }
        for f  in features:
            if f not in feature_map:
                raise ValueError(f"Feature {f} is not supported. Supported features are: {list(feature_map.keys())}")
            if len(unit_group) == 0:    
                raise ValueError("Unit group is empty. Please provide a valid unit group.")
            plot_func = feature_map[f]["func"]
            args = feature_map[f]["args"]
            plot_func(**args)
            img_buffer = io.BytesIO()
            plt.savefig(img_buffer, format="jpeg", dpi=300, bbox_inches='tight', transparent=True)
            plt.close()
            img_buffer.seek(0)
            encoded_img = base64.b64encode(img_buffer.getvalue()).decode('utf-8')
            encoded_images.append(encoded_img)
        img_array.append(encoded_images)
    df = pd.DataFrame(img_array, columns=features)
    df.index.name = "group_id"
    df.to_csv(save_path)
    return df

def plot_units_with_features(
    sortinganalyzer, 
    unit_ids=None, 
    features=UNIT_FEATURES,
    save=False,
    **kwargs
):
    if save:
        save_folder = os.path.join(sortinganalyzer.folder,'feature_plot')
        os.makedirs(save_folder, exist_ok=True)

    unit_ids_ = sortinganalyzer.unit_ids if unit_ids is None else unit_ids

    for unit_id in unit_ids_:
        feature_map = {
            "waveform_single": {"func": plot_waveform, "args": {"sortinganalyzer": sortinganalyzer, "unit_ids":[unit_id], "unit_colors":{unit_id: 'black'}, "alpha":1,"legend":False, "title":"Waveform single", "figsize":(5, 5), "peak_sign":'neg'}},
            "waveform_multi": {"func": plot_templates, "args" : {"sortinganalyzer": sortinganalyzer, "unit_ids":[unit_id], "unit_colors":{unit_id: 'black'}, "alpha":1,"legend":False, "title":"Waveform multi", "figsize":(5, 5), "num_channels":6}},
            "spike_locations": {"func": plot_spike_locations, "args":{"sortinganalyzer": sortinganalyzer, "unit_ids":[unit_id], "unit_colors":{unit_id: 'green'},"legend":False, "title":" Spike locations", "figsize":(5, 5), "margin":50, "with_channel_ids":True}},
            "amplitude_plot": {"func": plot_amplitude, "args":{"sortinganalyzer": sortinganalyzer, "unit_ids":[unit_id], "unit_colors":{unit_id: 'black'},"legend":False, "title":" Spike amplitude", "figsize":(15, 5), "y_lim":None}},
            "autocorr": {"func": plot_autocorrelogram,  "args":{"sortinganalyzer": sortinganalyzer, "unit_id":unit_id,"figsize":(4, 4),}},
        }
        width_ratios = [feature_map[f]["args"]["figsize"][0] for f in features]
        figsize = (sum(width_ratios),5)
        fig = plt.figure(figsize=figsize)
        plt.suptitle(f"Unit {unit_id}",fontsize=30)
        gs = gridspec.GridSpec(1, len(width_ratios), width_ratios=width_ratios)
        for grid,f in zip(gs,features):
            ax = plt.subplot(grid)
            plot_func = feature_map[f]["func"]
            args = feature_map[f]["args"]
            plot_func(**args, ax=ax)
        plt.tight_layout()
        
        if save:
            plt.savefig(os.path.join(save_folder, f"{unit_id}.png"), dpi=300, bbox_inches='tight')

def plot_waveform(sortinganalyzer, unit_ids=None, ax=None, unit_colors=None, alpha=1, legend=True, title="", figsize=(4, 4), peak_sign='neg'):    
    if sortinganalyzer.is_sparse():
        analyzer_sparsity = sortinganalyzer.sparsity
    else:
        # in this case, we construct a dense sparsity
        analyzer_sparsity = ChannelSparsity.create_dense(sortinganalyzer)

    if ax is None:
        fig, ax = plt.subplots(1, 1, figsize=figsize)    
    if unit_ids is None:
        unit_ids = sortinganalyzer.unit_ids
    if unit_colors is None:
        unit_colors = {unit_id: 'black' for unit_id in unit_ids}
    
    used_sparsity = analyzer_sparsity.from_best_channels(sortinganalyzer, num_channels=1)
    best_channels = used_sparsity.unit_id_to_channel_indices
    ext_templates = sortinganalyzer.get_extension("templates")
    templates = ext_templates.get_templates(unit_ids=unit_ids)
    spike_amps = sortinganalyzer.get_extension("spike_amplitudes").get_data(outputs="by_unit")[0]
    unit_amps = {unit_id: np.median(spike_amps[unit_id]) for unit_id in unit_ids}

    for i, unit_id in enumerate(unit_ids):
        chan_inds = best_channels[unit_id]
        template = templates[i, :, chan_inds]
        template_flat = template.flatten()
        ax.plot(template_flat, color=unit_colors[unit_id], alpha=alpha)
    ax.set_title(title)
    if legend:
        ax.legend([f'Unit {unit_id}' for unit_id in unit_ids], bbox_to_anchor=(1, 1),fontsize=10)

def plot_templates(sortinganalyzer, unit_ids=None, ax=None, unit_colors=None, alpha=1, figsize=(4, 4), legend=True, title="", num_channels=6):     
    if sortinganalyzer.is_sparse():
        analyzer_sparsity = sortinganalyzer.sparsity
    else:
        # in this case, we construct a dense sparsity
        analyzer_sparsity = ChannelSparsity.create_dense(sortinganalyzer)
    if unit_ids is None:
        unit_ids = sortinganalyzer.unit_ids
    if unit_colors is None:
        unit_colors = {unit_id: 'black' for unit_id in unit_ids}
    #used_sparsity = analyzer_sparsity.from_best_channels(sortinganalyzer, num_channels=num_channels)
    #sortinganalyzer.sparsity = used_sparsity

    sw.plot_unit_templates(
            sortinganalyzer, 
            unit_ids=unit_ids,
            ax=ax,
            unit_colors=unit_colors,
            same_axis=True,
            plot_legend=False,
            alpha_templates=alpha,
            shade_templates=False,
            set_title=False,
            axis_equal=False,
            plot_templates=True,
            figtitle=None if ax else title,
            figsize=figsize
        )
    if ax is not None:
        ax.set_title(title)
    if legend:
        plt.legend(fontsize=10, bbox_to_anchor=(1, 1))

def plot_spike_locations(sortinganalyzer, unit_ids=None, ax=None, unit_colors=None, alpha=1, figsize=(4, 4), legend=True, title="", margin=50, with_channel_ids=False):     
    if unit_ids is None:
        unit_ids = sortinganalyzer.unit_ids
    if ax is None:
        fig, ax = plt.subplots(1, 1, figsize=figsize)    
    if unit_colors is None:
        unit_colors = {unit_id: 'black' for unit_id in unit_ids}
    spike_locations_by_units = sortinganalyzer.get_extension('spike_locations').get_data(outputs="by_unit")
    sorting = sortinganalyzer.sorting
    segment_index=None
    if sorting.get_num_segments() > 1:
        assert segment_index is not None, "Specify segment index for multi-segment object"
    else:
        segment_index = 0
    x = []
    y = []
    for unit_id in unit_ids:
        spike_locs = spike_locations_by_units[segment_index][unit_id]
        x.append(np.mean(spike_locs['x']))
        y.append(np.mean(spike_locs['y']))
    x = np.mean(x)
    y = np.mean(y)
    sw.plot_spike_locations(
        sortinganalyzer,
        unit_ids=unit_ids,
        ax=ax,
        plot_legend=legend,
        with_channel_ids=with_channel_ids,
        unit_colors=unit_colors
    )
    ax.set_xlim(x - margin, x + margin)
    ax.set_ylim(y - margin, y + margin)
    ax.set_title(title)

def plot_amplitude(sortinganalyzer, unit_ids=None, ax=None, unit_colors=None, figsize=(10, 3), legend=True, title="",y_lim=None, plot_histograms =False): 
    if unit_ids is None:
        unit_ids = sortinganalyzer.unit_ids
    if unit_colors is None:
        unit_colors = {unit_id: 'black' for unit_id in unit_ids}
    sw.plot_amplitudes(
        sortinganalyzer, 
        unit_ids=unit_ids,
        ax=ax,
        plot_legend=legend,
        unit_colors=unit_colors,
        y_lim=y_lim,
        plot_histograms=plot_histograms,
        figsize=figsize,
        figtitle=None if ax else title
    )
    if ax is not None:
        ax.set_title(title)

def plot_autocorrelogram(sortinganalyzer, unit_id, ax=None, color='green', figsize=(4,4)):
    """Plot autocorrelogram for a single unit.

    Parameters
    ----------
    sortinganalyzer : SortingAnalyzer
    unit_id : int
    ax : matplotlib Axes | None
        If provided, draw on this axis; otherwise create a new figure.
    color : str
    figsize : tuple
    """
    if ax is None:
        fig, ax = plt.subplots(figsize=figsize)
    sw.plot_autocorrelograms(
        sortinganalyzer,
        unit_ids=[unit_id],
        unit_colors={unit_id: color},
        axes=[ax],
        backend='matplotlib'
    )
    ax.set_title(f"")
    return ax

def plot_crosscorrelograms(sortinganalyzer, unit_ids=None, title=""): 
    if unit_ids is None:
        unit_ids = sortinganalyzer.unit_ids
    sw.plot_crosscorrelograms(
        sortinganalyzer,
        unit_ids=unit_ids,
        figtitle=title
    )



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
    sortinganalyzer,
    encoded_img_df, 
    features=UNIT_FEATURES, 
    unit_ids = None,
    save = False,
    resize_height=1200
):
    for f in features:
        if f not in encoded_img_df.columns:
            raise ValueError(f'{f} not in img_df\nAvailable inputs: {encoded_img_df.columns.to_list()}')
    if save:
        save_folder = os.path.join(sortinganalyzer.folder,'feature_plot')
        os.makedirs(save_folder, exist_ok=True)

    unit_ids_ = sortinganalyzer.unit_ids if unit_ids is None else unit_ids

    for unit_id in unit_ids_:
        concatenated_img = concat_images_horizontally(encoded_img_df.loc[unit_id,features], resize_height)
        plt.figure(figsize=(12, 4))
        plt.imshow(concatenated_img)
        plt.title(f'Unit {unit_id}')
        plt.axis('off')
        plt.tight_layout()
        if save:
            plt.savefig(os.path.join(save_folder,f'unit_{unit_id}'), dpi = 300, bbox_inches='tight')

def plot_merge_with_features_df(
    sortinganalyzer,
    encoded_img_df, 
    features=MERGE_FEATURES, 
    group_ids = None,
    save = False,
    resize_height=300
):
    for f in features:
        if f not in encoded_img_df.columns:
            raise ValueError(f'{f} not in img_df\nAvailable inputs: {encoded_img_df.columns.to_list()}')
    if save:
        save_folder = os.path.join(sortinganalyzer.folder,'feature_plot')
        os.makedirs(save_folder, exist_ok=True)

    group_ids_ = encoded_img_df.index if group_ids is None else group_ids

    for group in group_ids_:
        concatenated_img = concat_images_horizontally(encoded_img_df.loc[group,features], resize_height)
        plt.figure(figsize=(12, 4))
        plt.imshow(concatenated_img)
        plt.title(f'Group {group}')
        plt.axis('off')
        plt.tight_layout()
        if save:
            plt.savefig(os.path.join(save_folder,f'group_{group}'))
            

def plot_rasters(sortinganalyzer, unit_ids=None, time_range = (0,100)):
    time_range_ = time_range
    if time_range is None:
        end = sortinganalyzer.get_total_duration()
        time_range_ = (0,end)
    unit_ids_ = unit_ids if unit_ids is not None else sortinganalyzer.unit_ids
    num_unit = len(unit_ids_)

    height_per_unit = 0.35
    max_height = 20
    fig_height = min(4 + num_unit * height_per_unit, max_height)
    figsize = (10, fig_height)

    fig, ax = plt.subplots(figsize=figsize)

    sw.plot_rasters(
        sorting=sortinganalyzer,
        unit_ids=unit_ids_,
        ax=ax,
        color="black",
        time_range = time_range_
    )

    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Unit")

    plt.tight_layout()

def plot_metrics_summary(sortinganalyzer, max_isi=1.5, min_snr=5.0):
    """
    Generate summary figure showing quality metrics and spike time locations.
    """
    metrics = sortinganalyzer.get_extension('quality_metrics').get_data()
    
    fig = plt.figure(figsize=(10, 10))
    grid = gridspec.GridSpec(3, 3, figure=fig, hspace=0.5, wspace=0.5)

    ax = fig.add_subplot(grid[0, 0:])
    sw.plot_rasters(
        sorting_analyzer=sortinganalyzer,
        ax=ax,color="black",
        time_range = (0,100),\
    )
    ax.set_xlim(0, 10)
    ax.set_yticks([])
    #ax.set_ylim(0, len(sortinganalyzer.channel_ids))
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
