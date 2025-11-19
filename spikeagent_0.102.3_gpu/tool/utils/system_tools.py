#import os
# def report_directory_contents(path: str, max_depth: int = 3, print_report: bool = True) -> str:
#     """
#     Recursively scans a directory up to a max_depth and returns a formatted
#     string reporting its contents as a tree.
#
#     Parameters
#     ----------
#     path : str
#         The absolute path to the directory.
#     max_depth : int
#         The maximum depth to scan. 0 means only the top-level contents.
#     print_report : bool
#         If True, print the report to stdout.
#
#     Returns
#     -------
#     str
#         A multi-line string describing the directory structure.
#     """
#     def _scan_dir(current_path, prefix="", depth=0):
#         lines = []
#         if depth > max_depth:
#             lines.append(f"{prefix}└── ... (max depth reached)")
#             return lines
#         
#         if not os.path.exists(current_path) or not os.path.isdir(current_path):
#             return [f"{prefix}Directory not found: {current_path}"]
#
#         try:
#             contents = sorted(os.listdir(current_path))
#         except OSError as e:
#             return [f"{prefix}Cannot access: {current_path} ({e.strerror})"]
#
#         if not contents:
#             return [] # Don't report empty directories for cleaner output
#
#         for idx, item in enumerate(contents):
#             item_path = os.path.join(current_path, item)
#             is_last = idx == len(contents) - 1
#             branch = "└──" if is_last else "├──"
#             sub_prefix = prefix + ("    " if is_last else "│   ")
#
#             if os.path.isdir(item_path):
#                 lines.append(f"{prefix}{branch} [Folder] {item}/")
#                 lines.extend(_scan_dir(item_path, sub_prefix, depth + 1))
#             else:
#                 lines.append(f"{prefix}{branch} [File]   {item}")
#         return lines
#
#     report_lines = [f"Contents of {path}:"]
#     if not os.path.exists(path) or not os.path.isdir(path):
#         report_lines.append(f"Directory not found: {path}")
#     else:
#         scan_results = _scan_dir(path)
#         if not scan_results:
#             report_lines.append("  (Directory is empty or contains only empty subfolders)")
#         else:
#             report_lines.extend(scan_results)
#
#     report = "\n".join(report_lines)
#     if print_report:
#         print(report)
#     return report


import os
import re
import numpy as np
import spikeinterface.full as si

def report_directory_contents(path: str,
    max_depth: int = 3,
    max_items_per_folder: int = 15,
    collapse_patterns: list = None,
    print_report: bool = True,
    show_summary: bool = True
) -> str:
    """
    Recursively scans a directory up to `max_depth`, formatting a tree-structured report.
    For folders with many subitems, collapses the listing (with patterns and item limits)
    to prevent overloading LLM or human readers, making this safe even for ultra-high-density
    electrode project folders (e.g., Neuropixels with 384 channels).

    Parameters
    ----------
    path : str
        Absolute path to the directory to scan.
    max_depth : int, optional
        Maximum depth to scan (default=3). 0 means only the root.
    max_items_per_folder : int, optional
        Maximum number of files/folders shown per folder. If exceeded, the middle of the list is collapsed.
    collapse_patterns : list of str, optional
        List of regex patterns. Folder names matching any pattern and present in large numbers (>5)
        will be collapsed into a single summary line.
        E.g., [r'pca_model_by_channel_local_\\d+']
    print_report : bool, optional
        If True, print the report to stdout.
    show_summary : bool, optional
        If True, print a summary line with total file/folder counts at the end.

    Returns
    -------
    str
        Multi-line string describing the tree structure and summary statistics.
    """
    if collapse_patterns is None:
        collapse_patterns = [r'pca_model_by_channel_local_\\d+']
    total_files = 0
    total_dirs = 0

    def _scan_dir(current_path, prefix="", depth=0):
        nonlocal total_files, total_dirs
        lines = []
        if depth > max_depth:
            lines.append(f"{prefix}└── ... (max depth reached)")
            return lines

        if not os.path.exists(current_path) or not os.path.isdir(current_path):
            return [f"{prefix}Directory not found: {current_path}"]

        try:
            contents = sorted(os.listdir(current_path))
        except OSError as e:
            return [f"{prefix}Cannot access: {current_path} ({e.strerror})"]

        # Collapse repetitive patterns
        for pattern in collapse_patterns:
            matches = [item for item in contents if re.match(pattern, item)]
            if len(matches) > 5:
                lines.append(f"{prefix}├── [Folder pattern: '{pattern}']: {len(matches)} folders, e.g. {matches[:2]} ... {matches[-2:]}")
                contents = [item for item in contents if item not in matches]

        # Limit items per folder for very large folders
        if len(contents) > max_items_per_folder:
            n = max_items_per_folder // 2
            shown = contents[:n] + ['...'] + contents[-n:]
            for item in shown:
                if item == '...':
                    lines.append(f"{prefix}├── ... ({len(contents) - max_items_per_folder} more items)")
                else:
                    item_path = os.path.join(current_path, item)
                    if os.path.isdir(item_path):
                        lines.append(f"{prefix}├── [Folder] {item}/")
                        total_dirs += 1
                    else:
                        lines.append(f"{prefix}├── [File]   {item}")
                        total_files += 1
        else:
            for idx, item in enumerate(contents):
                item_path = os.path.join(current_path, item)
                is_last = idx == len(contents) - 1
                branch = "└──" if is_last else "├──"
                sub_prefix = prefix + ("    " if is_last else "│   ")
                if os.path.isdir(item_path):
                    lines.append(f"{prefix}{branch} [Folder] {item}/")
                    total_dirs += 1
                    # Only recurse if not at max depth
                    if depth < max_depth:
                        lines.extend(_scan_dir(item_path, sub_prefix, depth + 1))
                else:
                    lines.append(f"{prefix}{branch} [File]   {item}")
                    total_files += 1
        return lines

    report_lines = [f"Contents of {path}:"]
    if not os.path.exists(path) or not os.path.isdir(path):
        report_lines.append(f"Directory not found: {path}")
    else:
        scan_results = _scan_dir(path)
        if not scan_results:
            report_lines.append("  (Directory is empty or contains only empty subfolders)")
        else:
            report_lines.extend(scan_results)

    if show_summary:
        report_lines.append(f"\nSummary: {total_files} files, {total_dirs} folders scanned (max_depth={max_depth})")
    report = "\n".join(report_lines)
    if print_report:
        print(report)
    return report

def get_automatic_depth_range(
    recording: si.BaseRecording,
    peak_locations: np.ndarray,
    window_um: float = 300.0
) -> tuple[float, float] | None:
    """
    Automatically determines an optimal depth range for plotting drift maps.

    It finds the median depth of detected peaks and creates a window of
    a specified size around it, clipped by the probe's physical boundaries.

    Parameters
    ----------
    recording : BaseRecording
        The recording object, used to get probe boundaries.
    peak_locations : np.ndarray
        The peak locations array from `compute_motion`.
    window_um : float, default: 300.0
        The total vertical size of the plotting window in micrometers.

    Returns
    -------
    tuple[float, float] | None
        A tuple with (min_depth, max_depth) for the plot, or None if it cannot be computed.
    """
    if not recording.has_probe():
        print("Warning: Cannot determine automatic depth range because no probe is attached.")
        return None
    
    if peak_locations is None or len(peak_locations) == 0:
        print("Warning: Cannot determine automatic depth range because no peak locations are available.")
        return None

    # 1. Get probe boundaries
    probe = recording.get_probe()
    probe_ymin, probe_ymax = probe.contact_positions[:, 1].min(), probe.contact_positions[:, 1].max()

    # 2. Find the median depth of all peaks
    all_peak_depths = peak_locations['y']
    median_depth = np.median(all_peak_depths)

    # 3. Calculate the window limits
    half_window = window_um / 2
    min_depth = median_depth - half_window
    max_depth = median_depth + half_window

    # 4. Clip the limits to the probe's physical boundaries
    min_depth_clipped = max(min_depth, probe_ymin)
    max_depth_clipped = min(max_depth, probe_ymax)
    
    print(f"Automatic depth range determined: ({min_depth_clipped:.0f}, {max_depth_clipped:.0f}) µm")
    
    return (min_depth_clipped, max_depth_clipped)
