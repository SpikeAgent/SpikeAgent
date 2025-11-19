#tool/utils/compute.py
from __future__ import annotations

import logging
from typing import Dict, Optional

import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import welch
from scipy.stats import median_abs_deviation  # local MAD implementation
import spikeinterface.full as si
import spikeinterface.widgets as sw
import spikeinterface.preprocessing as spre
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

def get_recording_summary_stats(recording, total_duration_s=10.0, seed=None):
    """
    Computes a robust, actionable summary of recording quality to guide preprocessing decisions.

    This function leverages SpikeInterface's efficient and robust methods to analyze:
    - Bad channel quality (using the IBL method)
    - Noise levels (using robust Median Absolute Deviation)
    - Power-line noise contamination
    - Shared noise across channels (for Common Reference decisions)
    - ADC saturation/clipping events

    Parameters
    ----------
    recording : BaseRecording
        The SpikeInterface recording object to analyze.
    total_duration_s : float, default: 10.0
        The total duration in seconds of random data to sample for the analysis.
    seed : int, optional
        A random seed for reproducibility.

    Returns
    -------
    dict
        A dictionary of summary statistics, ready for an AI agent to interpret.
    """
    if recording.get_num_samples() == 0:
        print("Warning: Recording is empty, cannot compute summary.")
        return {}

    fs = recording.get_sampling_frequency()
    n_channels = recording.get_num_channels()

    # --- 1. Robust Bad Channel Detection (IBL Method) ---
    # This provides a detailed breakdown of bad channels.
    try:
        bad_channel_ids, channel_labels = spre.detect_bad_channels(
            recording, method="coherence+psd", seed=seed
        )
        bad_channel_summary = {label: np.sum(channel_labels == label) for label in np.unique(channel_labels)}
    except Exception as e:
        print(f"Warning: `detect_bad_channels` failed with: {e}. Skipping this metric.")
        bad_channel_ids = []
        bad_channel_summary = {}

    # --- 2. Robust Noise Level Estimation (using Median Absolute Deviation) ---
    # `return_scaled=True` ensures we are working with physical units (uV).
    noise_levels_uv = si.get_noise_levels(recording, return_scaled=True, seed=seed)

    # --- 3. Efficiently Sample Data for other metrics using random chunks ---
    # This is memory-safe and provides a representative sample of the data.
    random_chunks_uv = si.get_random_data_chunks(
        recording,
        num_chunks_per_segment=20,
        chunk_duration=total_duration_s / 20,
        concatenated=True,
        return_scaled=True,
        seed=seed
    )

    # --- 4. Cross-Channel Correlation for CMR decision ---
    corr_matrix = np.corrcoef(random_chunks_uv.T)
    if n_channels > 1:
        iu = np.triu_indices(n_channels, k=1)
        # Median of absolute values is a robust measure of shared noise
        cross_channel_corr_abs_median = float(np.median(np.abs(corr_matrix[iu])))
    else:
        cross_channel_corr_abs_median = 0.0

    # --- 5. Power Spectrum Analysis for Line Noise ---
    nperseg = min(int(fs * 0.5), random_chunks_uv.shape[0])
    freqs, psd = welch(random_chunks_uv, fs=fs, axis=0, nperseg=nperseg)
    mean_psd_db = 10 * np.log10(np.mean(psd, axis=1) + 1e-12)

    def get_band_power_db(target_freq, bandwidth=2.0):
        idx = np.where((freqs >= target_freq - bandwidth / 2) & (freqs <= target_freq + bandwidth / 2))[0]
        return float(np.mean(mean_psd_db[idx])) if len(idx) > 0 else -np.inf

    # --- 6. Saturation/Clipping Detection ---
    # This must be done on raw integer data.
    saturation_events = 0
    if np.issubdtype(recording.get_dtype(), np.integer):
        unscaled_chunks = si.get_random_data_chunks(recording, return_scaled=False, concatenated=True,
                                                    num_chunks_per_segment=10, chunk_duration="1s", seed=seed)
        info = np.iinfo(recording.get_dtype())
        saturation_events = int(np.sum((unscaled_chunks >= info.max - 1) | (unscaled_chunks <= info.min + 1)))

    # --- 7. Assemble Final Actionable Summary ---
    summary = {
        "duration_s": recording.get_total_duration(),
        "sampling_frequency_hz": fs,
        "num_channels": n_channels,
        "median_noise_std_uv": float(np.median(noise_levels_uv)),
        "bad_channel_ids": bad_channel_ids,
        "bad_channel_summary": {k: int(v) for k, v in bad_channel_summary.items()},
        "cross_channel_correlation_median": cross_channel_corr_abs_median,
        "power_50hz_db": get_band_power_db(50.0),
        "power_60hz_db": get_band_power_db(60.0),
        "saturation_events_in_sample": saturation_events,
    }

    return summary



def inspect_recording_for_preprocessing(
    recording: si.BaseRecording,
    *,
    total_duration_s: float = 10.0,
    seed: Optional[int] = 123,
    bad_ch_factor: float = 5.0,
    corr_thresh: float = 0.97,
    plot: bool = True,
) -> Dict:
    """Return summary metrics (and optional figure) for a `SpikeInterface` recording.

    """

    # ------------------------------------------------------------------
    # 0. Early exits / constants
    # ------------------------------------------------------------------
    if recording.get_num_samples() == 0:
        raise ValueError("The provided recording contains no samples.")

    fs = recording.get_sampling_frequency()

    # ------------------------------------------------------------------
    # 1. Random data grab (scaled to µV)
    # ------------------------------------------------------------------
    random_chunks_uv = si.get_random_data_chunks(
        recording,
        num_chunks_per_segment=20,
        chunk_duration=total_duration_s / 20,
        concatenated=True,
        return_scaled=True,
        seed=seed,
    )

    ch_ids = recording.get_channel_ids()
    n_channels = ch_ids.size

    # ------------------------------------------------------------------
    # 2. Independent bad‑channel detectors
    # ------------------------------------------------------------------
    mad = median_abs_deviation(random_chunks_uv, axis=0)
    med_mad = float(np.median(mad))

    noise_hi = mad > bad_ch_factor * med_mad          # very noisy
    noise_lo = mad < 0.2 * med_mad                    # open / flat

    # --- neighbour correlation (shorts) ---
    corr = np.corrcoef(random_chunks_uv.T) if n_channels > 1 else np.zeros((1, 1))
    shorted = np.zeros(n_channels, dtype=bool)
    if n_channels > 2:
        idx = np.arange(1, n_channels - 1)
        left_corr = corr[idx, idx - 1]
        right_corr = corr[idx, idx + 1]
        shorted[idx] = (left_corr > corr_thresh) | (right_corr > corr_thresh)

    # --- saturation detector (integer data) ---
    sat = np.zeros(n_channels, dtype=bool)
    if np.issubdtype(recording.get_dtype(), np.integer):
        unscaled = si.get_random_data_chunks(
            recording,
            return_scaled=False,
            num_chunks_per_segment=10,
            chunk_duration=0.1,
            seed=seed,
        )
        info = np.iinfo(recording.get_dtype())
        sat = (
            np.mean((unscaled >= info.max - 1) | (unscaled <= info.min + 1), axis=0)
            > 0.005
        )

    # --- combine ---
    overall_bad = noise_hi | noise_lo | shorted | sat

    # ------------------------------------------------------------------
    # 3. Metrics & summary - REVISED TO RETURN CHANNEL IDS
    # ------------------------------------------------------------------
    summary: Dict[str, object] = {
        "median_noise_mad_uv": med_mad,
        "bad_channel_ids": ch_ids[overall_bad],
        "bad_channel_ids_by_type": {
            "noise_hi": ch_ids[noise_hi],
            "noise_lo": ch_ids[noise_lo],
            "shorted": ch_ids[shorted],
            "saturation": ch_ids[sat],
        },
        "bad_channel_summary": {
            "noise_hi": int(noise_hi.sum()),
            "noise_lo": int(noise_lo.sum()),
            "shorted": int(shorted.sum()),
            "saturation": int(sat.sum()),
            "good": int((~overall_bad).sum()),
        },
        "inter_sample_shift": recording.get_property("inter_sample_shift") is not None,
        "recording_by_group": recording.get_channel_groups() is not None,
    }

    # global correlation metric (same as before)
    if n_channels > 1:
        iu = np.triu_indices(n_channels, k=1)
        summary["cross_channel_correlation_median"] = float(np.median(np.abs(corr[iu])))
    else:
        summary["cross_channel_correlation_median"] = 0.0

    # ------------------------------------------------------------------
    # 4. PSD & line‑noise analysis
    # ------------------------------------------------------------------
    nperseg = min(int(fs * 2.0), random_chunks_uv.shape[0])
    freqs, psd_all = welch(random_chunks_uv, fs=fs, axis=0, nperseg=nperseg)
    mean_psd_db = 10 * np.log10(psd_all.mean(axis=1) + 1e-12)

    def _band_power(center: float, bw: float = 2.0) -> float:
        idx = (freqs >= center - bw / 2) & (freqs <= center + bw / 2)
        return float(np.mean(mean_psd_db[idx])) if np.any(idx) else -np.inf

    def _peak_prominence(center: float, bw: float = 2.0, surround_bw: float = 10.0) -> float:
        """Calculate how much a frequency peak stands out above surrounding frequencies."""
        peak_idx = (freqs >= center - bw / 2) & (freqs <= center + bw / 2)
        surround_idx = ((freqs >= center - surround_bw) & (freqs <= center - bw)) | \
                      ((freqs >= center + bw) & (freqs <= center + surround_bw))
        
        if not np.any(peak_idx) or not np.any(surround_idx):
            return 0.0
            
        peak_power = np.mean(mean_psd_db[peak_idx])
        surround_power = np.mean(mean_psd_db[surround_idx])
        return float(peak_power - surround_power)

    # Simple line noise assessment
    line_50hz_prominence = _peak_prominence(50.0)
    line_60hz_prominence = _peak_prominence(60.0)
    
    # Single robust recommendation: prominence > 10dB indicates significant line noise
    line_noise_detected = max(line_50hz_prominence, line_60hz_prominence) > 10.0
    
    summary["power_line_noise_db"] = {
        "50hz": _band_power(50.0),
        "60hz": _band_power(60.0),
        "50hz_prominence": line_50hz_prominence,
        "60hz_prominence": line_60hz_prominence,
        "line_noise_detected": line_noise_detected,
    }

    # ------------------------------------------------------------------
    # 5. Optional plot
    # ------------------------------------------------------------------
    fig = None
    if plot:
        fig, axes = plt.subplots(2, 3, figsize=(15, 9))
        fig.suptitle("Recording Quality Diagnostic Report", fontsize=18, fontweight="bold")

        # traces
        start_t = recording.get_time_info()["t_start"]
        sw.plot_traces(recording, time_range=(start_t, start_t+min(2, recording.get_duration())), ax=axes[0, 0])
        axes[0, 0].set_title("Sample Traces (first 2 s)")

        # PSD
        axes[0, 1].semilogx(freqs, mean_psd_db, color="darkcyan")
        axes[0, 1].set_title("Power Spectral Density")
        axes[0, 1].set_xlabel("Frequency (Hz)")
        axes[0, 1].set_ylabel("dB")
        axes[0, 1].grid(True, which="both", linestyle=":")

        # noise distribution plot
        axes[0, 2].hist(mad, bins=50, color="lightblue", alpha=0.7, edgecolor="black")
        axes[0, 2].axvline(med_mad, color="green", ls="-", linewidth=2, label=f"Median: {med_mad:.2f} µV")
        axes[0, 2].axvline(bad_ch_factor * med_mad, color="red", ls="--", linewidth=2, 
                          label=f"High noise thresh: {bad_ch_factor * med_mad:.2f} µV")
        axes[0, 2].axvline(0.2 * med_mad, color="orange", ls="--", linewidth=2, 
                          label=f"Low noise thresh: {0.2 * med_mad:.2f} µV")
        axes[0, 2].set_title("Noise Distribution (MAD)")
        axes[0, 2].set_xlabel("MAD (µV)")
        axes[0, 2].set_ylabel("Number of channels")
        axes[0, 2].legend(fontsize=8)
        axes[0, 2].grid(True, alpha=0.3)

        # correlation matrix
        im = axes[1, 0].imshow(corr, vmin=-1, vmax=1, cmap="coolwarm", aspect="auto")
        axes[1, 0].set_title("Cross‑Channel Correlation")
        fig.colorbar(im, ax=axes[1, 0], label="r")

        # correlation histogram
        if n_channels > 1:
            axes[1, 1].hist(corr[iu], bins=60, color="gray", alpha=0.7)
            med = summary["cross_channel_correlation_median"]
            axes[1, 1].axvline(med, color="red", ls="--", label=f"|median|={med:.3f}")
            axes[1, 1].axvline(-med, color="red", ls="--")
            axes[1, 1].legend()
        axes[1, 1].set_xlim(-1, 1)
        axes[1, 1].set_title("Correlation Coeff. Distribution")
        axes[1, 1].set_xlabel("r")
        axes[1, 1].set_ylabel("count")

        # channel quality summary bar plot
        categories = list(summary["bad_channel_summary"].keys())
        counts = list(summary["bad_channel_summary"].values())
        colors = ["red", "orange", "purple", "darkred", "green"]
        bars = axes[1, 2].bar(categories, counts, color=colors, alpha=0.7)
        axes[1, 2].set_title("Channel Quality Summary")
        axes[1, 2].set_ylabel("Number of channels")
        axes[1, 2].tick_params(axis='x', rotation=45)
        
        # Add count labels on bars
        for bar, count in zip(bars, counts):
            if count > 0:
                axes[1, 2].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1,
                               str(count), ha='center', va='bottom', fontweight='bold')

        plt.tight_layout(rect=[0, 0.03, 1, 0.95])
        plt.show()
        for key, value in summary.items():
            print(f"{key}: {value}")

    return (summary, fig) if plot else summary

def get_groups_from_recording(recording):
    """
    Takes a recording object and returns a list of lists of channel IDs,
    formatted correctly for the 'groups' argument in functions like 
    `spikeinterface.common_reference`.

    Parameters
    ----------
    recording : BaseRecording
        The recording object from which to extract channel groups.

    Returns
    -------
    list[list]
        A list where each inner list contains the channel IDs for one group.
        Returns None if no grouping information is present on the recording.
    """
    if "group" not in recording.get_property_keys():
        return None
        
    group_assignments = recording.get_channel_groups()
    channel_ids = recording.get_channel_ids()
    
    unique_group_ids = np.unique(group_assignments)
    
    groups = []
    for group_id in unique_group_ids:
        indices_in_group = np.where(group_assignments == group_id)[0]
        channels_in_group = channel_ids[indices_in_group]
        groups.append(list(channels_in_group))
        
    return groups

