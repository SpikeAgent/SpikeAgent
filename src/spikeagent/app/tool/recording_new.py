# This file (recording_new.py) is now the canonical source for all guidance-based tools for loading and saving recordings.
# It replaces the old recording.py, which is now deprecated and retained only for legacy compatibility.
# tool/recording.py
from textwrap import dedent
from typing import Literal
import re

__all__ = [
    "get_guidance_on_loading_recording",
    "get_guidance_on_loading_raw_data",
    "get_guidance_on_saving_recording",
]

def get_guidance_on_loading_recording(
    detailed_reasoning: str,
    code: str
) -> str:
    """
    This function formats the `detailed_reasoning` and `code` that you, the SpikeAgent, provide for loading a processed recording.

    Your task is to:
    1.  **Generate Reasoning**: Create a `detailed_reasoning` string that explains your plan.
    2.  **Construct Code**: Use the `<Code Snippet for loading saved recording>` template below to create the `code` string.
    3.  **Call this function**: Pass the `detailed_reasoning` and `code` strings you just created as arguments.

    The function will then return the combined, formatted output.

    **IMPORTANT**: The code snippet is a template. You are flexible in assembling the code. You can use parts of it, assemble new code, change the variable name based on the context, or even provide no code if the user's intent cannot be addressed by this template. Your primary goal is to fulfill the user's request effectively.

    <Code Snippet for loading saved recording>
    # --- SIMPLE VERSION (for quick loads) ---
    import spikeinterface.full as si
    import spikeinterface.widgets as sw
    import os
    # Agent should list folder contents of the processed_folder with python_repl_tool and see the contents and see if the recording folder exists.
    # some time user may provide the recording folder name. if so you can try to load it directly.
    recording_folder = os.path.join(processed_folder, 'recording')
    recording = si.load(recording_folder)
    print("Recording loaded.")

    # --- ROBUST VERSION (for pipeline or user feedback) ---
    import spikeinterface.widgets as sw
    if recording.has_probe():
        sw.plot_probe_map(recording, with_channel_ids=True)
        print("Probe map plotted.")
    else:
        print("Warning: Loaded recording does not have a probe attached.")
    print(recording)
    </Code Snippet for loading saved recording>

    <Instruction for SpikeAgent>
        <dependencies>
            - The 'recording' folder must exist in the `processed_folder`.
            - The environment setup (Step 1) must be complete.
        </dependencies>
        <execution_modes>
            <mode name="pipeline">
                <description>Loads a previously saved and processed SpikeInterface recording as part of the standard pipeline.</description>
                <action>
                    1.  **Execute Code**: Use the ROBUST version from the code snippet to load the recording and plot the probe map for validation.
                    2.  **Validate**: Confirm that the recording is loaded and the probe map is plotted (or a warning is printed if no probe exists).
                    3.  **Confirm with User**: Announce the completion of Step 2 and ask to proceed to Step 3.
                </action>
            </mode>
            <mode name="standalone">
                <description>For quick, one-off loads when the user wants to inspect a saved recording.</description>
                <action>
                    1.  **Execute Code**: Use the SIMPLE version from the code snippet.
                    2.  **Inform User**: Announce that the recording has been loaded and wait for the next command.
                </action>
            </mode>
        </execution_modes>
    </Instruction for SpikeAgent>
    """
    return dedent(detailed_reasoning) + '\n\n' + dedent(code)


def get_guidance_on_loading_raw_data(
    detailed_reasoning: str,
    code: str
) -> str:
    """
    This function formats the `detailed_reasoning` and `code` for loading raw e-phys data. The `data_format` parameter guides you on which template to use.

    Parameters
    ----------
    data_format : str
        The format of the raw data, one of "neuropixels", "intan_rhd", or "spikeinterface_binary".

    Your task is to:
    1.  **Select Template**: Choose the appropriate code snippet below based on the `data_format`.
    2.  **Generate Reasoning**: Create a `detailed_reasoning` string explaining your plan.
    3.  **Construct Code**: Adapt the chosen template to create the `code` string.
    4.  **Call this function**: Pass all required arguments.

    **IMPORTANT**: You are flexible in assembling the code. You can use parts of it, assemble new code, change the variable name based on the context, or even provide no code if the user's intent cannot be addressed by this template.

    --- TEMPLATES FOR RAW DATA LOADING ---

    <Guidance for Loading Raw Data: Neuropixels>
    **Goal**: Load raw Neuropixels (SpikeGLX) data.
    **Instructions**: Review file list, identify the 'ap' stream, and adapt the code.
    <Code Snippet for loading raw neuropixels data>
    import spikeinterface.extractors as se
    stream_names, _ = se.get_neo_streams('spikeglx', raw_data_path)
    ap_stream_name = next((s for s in stream_names if 'ap' in s), None)
    if ap_stream_name:
        recording = se.read_spikeglx(raw_data_path, stream_name=ap_stream_name)
        print("Neuropixels recording loaded successfully:")
        print(recording)
        print(f"Probe attached automatically: {recording.has_probe()}")
    else:
        print("Error: Could not identify an 'ap' stream in the raw data folder.")
    </Code Snippet for loading raw neuropixels data>
    - If the probe is not attached, you will need to ask the user for a probe file before saving.
    </Guidance for Loading Raw Data: Neuropixels>

    <Guidance for Loading Raw Data: Intan RHD>
    **Goal**: Load raw Intan RHD data.
    **Instructions**: Review file list and use the following code.
    <Code Snippet for loading raw intan data>
    from spikeagent.app.tool.utils.read_file import read_rhd_to_recording
    recording = read_rhd_to_recording(folder_path=raw_data_path)
    print("Intan recording loaded successfully:")
    print(recording)
    print(f"Probe attached automatically: {recording.has_probe()}")
    </Code Snippet for loading raw intan data>
    - If the probe is not attached, you will need to ask the user for a probe file before saving.
    </Guidance for Loading Raw Data: Intan RHD>

    <Guidance for Loading Raw Data: nwb file>
    **Goal**: Load raw Intan RHD data.
    **Instructions**: Review file list and use the following code. fs is set to 24414.0625 by default.
    <Code Snippet for loading raw intan data>
    from spikeagent.app.tool.utils.read_file import read_nwb_to_recording
    reocording = convert_nwb_to_recording(
        folder_path=raw_data_path,
        fs=24414.0625,
        chunk_samp=200_000,
        overwrite=True
    )
    print("NWB recording loaded successfully:")
    print(recording)
    print(f"Probe attached automatically: {recording.has_probe()}")
    </Code Snippet for loading raw intan data>
    - If the probe is not attached, you will need to ask the user for a probe file before saving.
    </Guidance for Loading Raw Data: Intan RHD>

    <Guidance for Loading Raw Data: SpikeInterface Binary>
    **Goal**: Load a SpikeInterface BinaryRecording.
    <Code Snippet for loading SpikeInterface Binary>
    import spikeinterface.full as si
    recording = si.load(raw_data_path)
    print("Loaded SpikeInterface BinaryRecording:")
    print(recording)
    print(f"Probe attached automatically: {recording.has_probe()}")
    </Code Snippet for loading SpikeInterface Binary>
    - If the probe is not attached, you will need to ask the user for a probe file before saving.
    </Guidance for Loading Raw Data: SpikeInterface Binary>

    <Instruction for SpikeAgent>
        <dependencies>
            - The data format must be identified in Step 1.
        </dependencies>
        <execution_modes>
            <mode name="pipeline">
                <description>Loads raw e-phys data from formats like Neuropixels or Intan as part of the main pipeline.</description>
                <action>
                    1.  **Execute Code**: Adapt and execute the relevant code snippet for the identified `data_format`.
                    2.  **Validate**: Confirm the `recording` object is created and its "Probe attached" status is printed.
                    3.  **Probe Handling**:
                        - If the probe is already attached, proceed to Step 5.
                        - If the probe is not attached, you must ask the user for a `probe_path`.
                    4.  **Pre-flight Channel Check (if probe_path was provided)**:
                        - **Generate and execute a pre-flight check.** You must run a code snippet *before* calling the save tool to compare the recording and probe channel counts.
                        - **Code Example**:
                          
                            from probeinterface import read_probeinterface
                            probe = read_probeinterface("{user_provided_probe_path}")
                            probe_chans = probe.get_contact_count()
                            rec_chans = recording.get_num_channels()
                            print(f"Probe channels: {probe_chans}, Recording channels: {rec_chans}")
                            if probe_chans != rec_chans:
                                print("MISMATCH_DETECTED")
                          
                        - **If `MISMATCH_DETECTED`**:
                            - Announce the mismatch to the user.
                            - **You must now ask the user for the `block_channels`** required to resolve the difference.
                            - Once you have the `block_channels`, proceed to the final step.
                        - **If counts match**:
                            - Announce that the channel counts match and you will proceed with an empty `block_channels` list.
                    5.  **Next Step**: Once all parameters are validated and collected, call `get_guidance_on_saving_recording`.
                </action>
            </mode>
        </execution_modes>
    </Instruction for SpikeAgent>
    """
    return dedent(detailed_reasoning) + '\n\n' + dedent(code)

def get_guidance_on_saving_recording(
    detailed_reasoning: str,
    code: str
) -> str:
    """
    This function formats the `detailed_reasoning` and `code` for saving a recording.

    Parameters
    ----------
    block_channels : list
        List of channel IDs to exclude. Can be an empty list.
    probe_path : str | None
        Path to a probe file (.json), required only if a probe is not already attached.

    Your task is to:
    1.  **Generate Reasoning**: Create a `detailed_reasoning` string explaining your plan.
    2.  **Construct Code**: Use the template below to create the `code` string. You MUST replace `YOUR_BLOCK_CHANNELS_LIST` and `YOUR_PROBE_PATH_STRING` with the actual values for `block_channels` and `probe_path` respectively. Remember that `probe_path` should be a string literal in the code (e.g., `'path/to/probe.json'` or `None`).
    3.  **Call this function**: Pass all required arguments.

    **IMPORTANT**: You are flexible in assembling the code. You can use parts of it, assemble new code, change the variable name based on the context, or even provide no code if the user's intent cannot be addressed by this template.

    <Code Snippet for saving processed recording>
    # --- SIMPLE VERSION (for quick saves, e.g., after filtering) ---
    import spikeinterface.full as si
    import spikeinterface.widgets as sw
    import os

    recording_folder = os.path.join(processed_folder, 'recording')
    recording.save(folder=recording_folder, n_jobs=-1, overwrite=True)
    print("Recording saved.")

    # --- ROBUST VERSION (for initial save or when changing channels/probe) ---
    from probeinterface import read_probeinterface
    import os

    # Inject user-provided parameters so they exist inside the runtime namespace
    block_channels = YOUR_BLOCK_CHANNELS_LIST  # e.g., [20, 21] or ['CH1', 'CH2']
    probe_path = YOUR_PROBE_PATH_STRING    # e.g., "None" or "'/path/to/probe.json'"

    can_save = True
    # --- 1. Handle bad / excluded channels ---
    if block_channels:
        valid_channel_ids = list(recording.get_channel_ids())
        invalid_channels = [ch for ch in block_channels if ch not in valid_channel_ids]
        if invalid_channels:
            can_save = False
            print(f"ERROR: The following channel IDs in `block_channels` are invalid: {invalid_channels}")
            print(f"Available channel IDs are: {valid_channel_ids}")
            print("AGENT_ACTION: You MUST ask the user to provide a corrected list of `block_channels` "
                  "before trying again.")
        else:
            selected_channels = [ch for ch in recording.channel_ids if ch not in block_channels]
            recording = recording.select_channels(selected_channels)
            print(f"Blocked channels: {block_channels}. Remaining: {recording.get_num_channels()} channels.")
    else:
        print("No channels were blocked.")

    # --- 2. Attach probe if needed ---
    if can_save and not recording.has_probe() and probe_path:
        if not os.path.exists(probe_path):
            print(f"ERROR: Probe file not found at {probe_path}.")
        else:
            probegroup = read_probeinterface(probe_path)
            # Check for channel count mismatch
            if probegroup.get_contact_count() != recording.get_num_channels():
                print(f"ERROR: Probe channel count ({probegroup.get_contact_count()}) "
                      f"does not match recording channel count ({recording.get_num_channels()}).")
                print("AGENT_ACTION: You MUST ask the user to provide a list of `block_channels` to exclude "
                      "so the channel counts match before trying again.")
                can_save = False
            else:
                recording.set_probegroup(probegroup, in_place=True)
                print(f"Probe attached successfully from {probe_path}.")

    # --- 3. Save to disk (only if probe is valid) ---
    import spikeinterface.full as si
    if can_save:
        recording_folder = os.path.join(processed_folder, 'recording')
        recording.save(folder=recording_folder, n_jobs=-1, overwrite=True)
        print(f"Recording successfully saved to: {recording_folder}")

        recording = si.load(recording_folder)
        print("Reloaded saved recording for verification:")
        print(recording)
    else:
        print("SAVE_SKIPPED: Recording was NOT saved due to previous errors.")

    # --- 4. Plot probe map) ---
    if recording.has_probe():
        sw.plot_probe_map(recording, with_channel_ids=True)
    </Code Snippet for saving processed recording>

    <Instruction for SpikeAgent>
        <dependencies>
            - A `recording` object must exist in the workspace.
            - `block_channels` and `probe_path` parameters must be defined (even if empty or None).
        </dependencies>
        <execution_modes>
            <mode name="pipeline">
                <description>
    Saves the loaded raw recording to a standardized SpikeInterface binary format.
    This tool handles channel exclusion via the `block_channels` parameter, which is primarily used to match the recording's channel count to a probe file before attachment. It also handles attaching the probe itself.
                </description>
                <action>
                    1.  **Execute Code**: Use the ROBUST version from the code snippet. This code will first use the `block_channels` parameter you collected to select the correct channels before attempting to attach the probe and save.
                    2.  **Validate**: After execution, confirm that the recording was saved successfully and that the probe map was plotted.
                    3.  **Error Handling**: The code snippet has a built-in check. If the output contains a `SAVE_SKIPPED` error, it means the channel counts still do not match. You must stop, re-ask the user for the correct `block_channels` list, and then call this tool again with the corrected list.
                    4.  **Next Step**: After a successful save, call `get_guidance_on_recording_summary` to begin Step 3.
                </action>
            </mode>
            <mode name="standalone">
                <description>For quick re-saves after minor processing, if no channel or probe changes are needed.</description>
                <action>
                    - Execute the SIMPLE version of the code snippet.
                </action>
            </mode>
        </execution_modes>
    </Instruction for SpikeAgent>
    """
    return dedent(detailed_reasoning) + '\n\n' + dedent(code)



