# tool/preprocessing_new.py
from textwrap import dedent

__all__ = [
    "get_guidance_on_recording_summary",
    "get_guidance_on_preprocessing",
    "get_guidance_on_preprocessing_comparison",
    "get_guidance_on_motion_correction",
]


def get_guidance_on_motion_correction(
    detailed_reasoning: str,
    code: str
) -> str:
    """
    Provides guidance for a motion correction experiment and formats the agent's response.

    This tool guides you, the SpikeAgent, through an experiment to find the best motion
    correction preset. The process involves computing motion for several presets, visually
    inspecting the results with an automatic zoom depth range, and then autonomously
    deciding which preset is best before applying the correction.

    Your task is to:
    1.  **Generate Reasoning**: Create a `detailed_reasoning` string explaining your plan.
    2.  **Construct Code**: Use the template below to create the `code` string.
    3.  **Call this function**: Pass the `detailed_reasoning` and `code` strings.

    **IMPORTANT**: The code is a template. You are flexible in assembling it. You can use parts, assemble new code, or change variable names.

    <Code Snippet and instructions for motion correction experiment>
    import spikeinterface.full as si
    import os
    import matplotlib.pyplot as plt
    import numpy as np
    import shutil
    from spikeagent.app.tool.utils.system_tools import get_automatic_depth_range

    # --- Motion Correction Task 1: Run experiment for multiple presets ---
    base_motion_folder = os.path.join(processed_folder, "motion_correction")
    if os.path.exists(base_motion_folder):
        shutil.rmtree(base_motion_folder)

    presets_to_test = ("rigid_fast", "kilosort_like", "nonrigid_accurate","dredge_fast")
    motion_results = {}

    # Conditionally set rigid parameter based on probe depth range
    try:
        probe = recording.get_probe()
        contact_positions = probe.contact_positions
        depth_range = np.ptp(contact_positions[:, 1])
        print(f"Probe depth range detected: {depth_range:.2f} µm")
        is_rigid = depth_range < 1500
    except Exception:
        is_rigid = True # Default to rigid if probe info is not available

    estimate_motion_kwargs = {'rigid': is_rigid}
    print(f"Motion estimation will be run with rigid={is_rigid}")

    for preset in presets_to_test:
        print(f"\\n--- Computing motion with preset: '{preset}' ---")
        folder = os.path.join(base_motion_folder, preset)
        motion, motion_info = si.compute_motion(
            recording,
            preset=preset,
            folder=folder,
            output_motion_info=True,
            n_jobs=-1,
            progress_bar=True,
            estimate_motion_kwargs=estimate_motion_kwargs
        )
        motion_results[preset] = {'motion': motion, 'motion_info': motion_info}

    # --- Motion Correction Task 2: Plot all results for visual comparison ---
    for preset, results in motion_results.items():
        print(f"\\n--- Plotting results for preset: '{preset}' ---")
        motion_info = results['motion_info']
        peak_locations = motion_info.get('peak_locations')
        
        auto_depth_lim = get_automatic_depth_range(
            recording=recording,
            peak_locations=peak_locations,
            window_um=400.0
        )

        fig = plt.figure(figsize=(14, 8))
        si.plot_motion_info(
            motion_info,
            recording,
            figure=fig,
            depth_lim=auto_depth_lim,
            amplitude_alpha=0.7,
            color_amplitude=True,
            amplitude_cmap="inferno",
            scatter_decimate=10,
        )
        fig.suptitle(f"Motion Correction Results: preset='{preset}' (Auto-Zoomed)")
        plt.show()

    # --- STOP POINT: END OF TURN ---
    # The agent's code execution for this turn MUST end here.
    # The agent now needs to stop, receive all the plots from the experiment,
    # and begin a NEW turn to execute the decision-making logic below.
    # ----------------------------------------------------

    # --- Motion Correction Task 3 (NEXT TURN): Make a decision ---
    # After inspecting all the plots, you must now start a new turn to make a
    # two-part decision. 
    # First, is correction needed at all? 
    # Second, if so, check the peak depth plot to reason first and then decide which preset is best?

    # --- Example if motion is NOT significant ---
    # print("Decision: After visual inspection, the motion vectors show a maximum drift of less than 30 µm. No correction is necessary.")
    # # No action is taken, the agent will move to the next step with the current `recording` object.
    # -----------------------------------------------

    # --- Example if you choose 'kilosort_like' ---
    # print("The reason why you choose kilosort") print the reason why you choose kilosort_like
    # from spikeinterface.sortingcomponents.motion import interpolate_motion
    # chosen_preset = 'kilosort_like'
    # motion_folder = os.path.join(base_motion_folder, chosen_preset)
    # motion_info = si.load_motion_info(motion_folder)
    # motion = motion_info['motion']
    # recording = interpolate_motion(recording=recording, motion=motion)
    # -----------------------------------------------

    # --- Example if you choose 'nonrigid_accurate' ---
    # print("The reason why you choose nonrigid_accurate") print the reason why you choose nonrigid_accurate
    # from spikeinterface.sortingcomponents.motion import interpolate_motion
    # chosen_preset = 'nonrigid_accurate'
    # motion_folder = os.path.join(base_motion_folder, chosen_preset)
    # motion_info = si.load_motion_info(motion_folder)
    # motion = motion_info['motion']
    # recording = interpolate_motion(recording=recording, motion=motion)
    # ----------------------------------------------------
    </Code Snippet and instructions for motion correction experiment>

    <Instruction for SpikeAgent>
        <dependencies>
            - A `recording` object must exist in the workspace.
            - A `processed_folder` variable (str) must be defined.
        </dependencies>
        <execution_modes>
            <mode name="pipeline">
                <description>When you are at the motion correction stage of the preprocessing pipeline.</description>
                <action>
                    1. First reason and explain to the user your plan before you execute the code snippet with `python_repl_tool`to run the multi-preset experiment and generate all comparison plots.
                    2. **STOP and end your turn.**
                    3. After receiving the plots, **start a new turn.**
                    4. **Visually analyze all plots.** First, check the "Motion vectors" to decide if drift is significant (>30um). If it is, then compare the "Peak depth" plots to find the best preset.
                    5. **State your decision and reasoning.** Announce whether you will apply a correction, and if so, which preset you have chosen. ALWAYS reason first and then decide.
                    6. **Generate and execute the final code** to apply the chosen motion correction (or do nothing). Then, proceed to the next step.
                </action>
            </mode>
            <mode name="standalone">
                <description>When the user asks to check for drift or motion.</description>
                <action>
                    1. **Check workspace state.** Silently review your execution history to see if a `recording` object and a `processed_folder` variable exist.
                    2. **If dependencies are NOT met:** Announce that you must load data first. For example: "To check for drift, I first need to load a recording." Then, call the necessary setup tools (`get_guidance_on_environment_setup`, etc.) and get user confirmation to proceed.
                    3. **Once dependencies are met:** Announce you are starting the experiment. Execute the code to generate all comparison plots.
                    4. **STOP and end your turn.**
                    5. After receiving the plots, **start a new turn.**
                    6. **Visually analyze all plots** and state your conclusion about the best preset.
                    7. **Ask the user** if they would like to apply the correction by creating a new motion-corrected `recording` object.
                </action>
            </mode>
        </execution_modes>
    </Instruction for SpikeAgent>
    """
    return dedent(detailed_reasoning) + '\n\n' + dedent(code)


def get_guidance_on_preprocessing(
    detailed_reasoning: str,
    code: str
) -> str:
    """
    Provides guidance for building a data-driven preprocessing pipeline and formats the agent's response.

    This tool guides you, the SpikeAgent, through designing and executing a multi-step
    preprocessing pipeline. You will use metrics from an initial recording summary to justify
    and assemble the pipeline, which can include bad channel removal, filtering, phase-shift
    correction, and a Common Mode Rejection (CMR) experiment.

    Your task is to:
    1.  **Generate Reasoning**: Create a `detailed_reasoning` string explaining your plan.
    2.  **Construct Code**: Use the template below to create the `code` string.
    3.  **Call this function**: Pass the `detailed_reasoning` and `code` strings.

    **IMPORTANT**: You are flexible in assembling the code. Adapt it based on your data-driven decisions.

    <Guidance for Building a Preprocessing Pipeline>
    **Your Mission**: You are an expert SpikeAgent. Your goal is to design and execute
    a comprehensive preprocessing pipeline. You must justify every step by referencing
    the specific metrics and visual evidence from the initial diagnostic summary.

    ---
    **IMPORTANT CONCEPTS FOR THE SpikeAgent**

    1.  **Your Code is a Template**: The code snippets are adaptable examples. You must assemble the final code based on your data-driven decisions.

    2.  **State is Persistent**: Variables you create (like the `recording` object) persist.
    ---
    <Code Snippet and instructions for general probe preprocessing>
    # This is a template. The agent must decide which of these steps are necessary,
    # run the CMR experiment if needed, and then assemble the final code block.
    from spikeagent.app.tool.utils.compute import inspect_recording_for_preprocessing, get_groups_from_recording
    import spikeinterface.preprocessing as spre

    print("Designing a data-driven preprocessing pipeline for a general probe…")

    # --- Agent's Plan (to be generated by the agent) ---
    # Preprocessing Task 1: Announce the full, multi-step plan based on initial analysis.
    # Preprocessing Task 2: Assemble and execute the code for initial cleanup (bad channels, phase shift, filtering).
    # Preprocessing Task 3: If needed, run the Common Mode Rejection (CMR) experiment.
    # Preprocessing Task 4 (NEXT TURN): After visual inspection, announce the winning CMR strategy.
    # Preprocessing Task 5 (NEXT TURN): Generate and execute the final line of code to apply the chosen CMR.
    # ----------------------------------------------------------------

    # --- Template for Initial Cleanup (Preprocessing Task 2) ---
    # The agent must use its analysis of the summary to decide which of the
    # following steps are necessary and what parameters to use. These are examples.
    # recording_processed = recording.remove_channels(...) # if bad_channel_ids is not empty
    # if "inter_sample_shift" in recording.get_property_keys():
    #   recording_processed = spre.phase_shift(recording_processed) # if there is a phase shift
    # recording_processed = spre.notch_filter(recording_processed, freq=...) # if there is a line noise
    # recording_processed = spre.bandpass_filter(recording_processed, freq_min=300, freq_max=6000) # NOTE: freq_max cannot exceed half of the recording's sampling frequency.
    # If you hit an error with bandpass_filter, you can use spre.highpass_filter(recording, freq_min=300) as a fallback.
    # -------------------------------------------------

    # --- Template for CMR Experiment (Preprocessing Task 3) ---
    # The agent generates this block if its initial visual analysis indicated CMR is needed.
    # This is triggered by seeing "blocky" patterns in the correlation matrix, even if correlation values aren't very high.
    # print("\\n--- Starting CMR Experiment ---")
    # cmr_strategies = {'global': {'reference': 'global', 'groups': None},
    #                   'local_proximity': {'reference': 'local', 'groups': None}}
    #
    # if summary.get('recording_by_group'):
    #     print("Probe has groups, will also test CMR by group.")
    #     groups = get_groups_from_recording(recording_processed)
    #     cmr_strategies['grouped_global'] = {'reference': 'global', 'groups': groups}
    #
    # cmr_results = {}
    # for name, params in cmr_strategies.items():
    #     print(f"\\n--- Testing {name.upper()} CMR ---")
    #     rec_test = spre.common_reference(recording_processed, operator='median', **params)
    #     summary_test, _ = inspect_recording_for_preprocessing(rec_test, plot=True)
    #     cmr_results[name] = {'summary': summary_test, 'recording': rec_test}
    # ----------------------------------------------------

    # --- STOP POINT: END OF TURN ---
    # The agent's code execution for this turn MUST end here.
    # The agent now needs to stop, receive the plots from the experiment,
    # and begin a NEW turn to execute the decision-making logic below.
    # ----------------------------------------------------

    # --- Agent's Visual Decision (Preprocessing Tasks 4 & 5 - NEXT TURN) ---
    # After inspecting all the plots from the experiment, you must now start a
    # new turn, generate code to announce your decision, and apply it. Your
    # choice MUST be one of the strategies that were tested. Below are examples
    # for EACH possible outcome.

    # --- Example if Agent choose GLOBAL CMR ---
    # recording_processed = cmr_results['global']['recording']
    # recording = recording_processed
    # -----------------------------------------

    # --- Example if Agent choose LOCAL (PROXIMITY) CMR ---
    # recording_processed = cmr_results['local_proximity']['recording']
    # recording = recording_processed
    # ---------------------------------------------------

    # --- Example if Agent choose GROUPED GLOBAL CMR ---
    # recording_processed = cmr_results['grouped_global']['recording']
    # recording = recording_processed
    # ------------------------------------------------

    # --- Example if NO CMR is better ---
    # print("Decision: After visual inspection, none of the CMR strategies provided a clear improvement. No CMR will be applied.")
    # recording = recording_processed # The one from before the experiment
    # -------------------------------------

    </Code Snippet and instructions for general probe preprocessing>

    <Instruction for SpikeAgent>
        **Your Mission**: Your goal is to design and execute a data-driven preprocessing pipeline, justifying every step with evidence from the initial summary.

        **CRITICAL NOTE ON VARIABLES**: The final processed recording object is named `recording_processed` in the templates. For the changes to persist for later pipeline steps, you MUST reassign it back to the main `recording` variable at the very end of all preprocessing. Example: `recording = recording_processed`

        ---
        **Decision-Making Rules**
        ---
        You must build a pipeline by checking each condition below, using both the summary metrics and the visual plots you have analyzed.
        - **1. Bad-channel handling**: Check `bad_channel_ids`. If not empty, the first step is to remove them. Justify this by stating the number and type of bad channels found. **NOTE**: These `bad_channels` are detected based on poor signal quality, which is different from the `block_channels` used during initial loading to match probe layouts.
        - **2. Phase-shift correction**: Check `inter_sample_shift`. If `True`, the next step is `spre.phase_shift`. Explain its importance.
        - **3. Line-noise filtering**: Check `line_noise_detected`. If `True`, add a `spre.notch_filter`, choosing the frequency based on the `prominence` values.
        - **4. Band-pass filtering**: Always add a `spre.bandpass_filter` or `spre.highpass_filter` after the initial cleanup steps.
        - **5. Common Reference (CMR) Experiment**: 
            - **Visual Trigger**: IMPORTANT: If the correlation matrix heatmap contains noticeable contiguous square or rectangular regions (typically symmetric across the diagonal) where many adjacent channels have similar strong correlation values 
                      — appearing as uniform-colored blocks rather than scattered fine-grained patterns — this indicates shared-noise structure. This condition should trigger a CMR experiment even if the overall correlation values are modest. 
                      LOOK AT THE HEATMAP TOO OVER THE CORRELATION VALUES. HEATMAP IS MORE IMPORTANT THAN THE CORRELATION VALUES.
            - **Run Full Experiment**: If the experiment is needed, test all applicable strategies by generating and inspecting plots:
                - **Strategy 1: Global CMR**: `reference='global'`.
                - **Strategy 2: Local CMR**: `reference='local'` (uses proximity).
                - **Strategy 3: Grouped CMR**: If `summary.get('recording_by_group')` is `True`, you MUST also test `reference='global'` with `groups=...` to perform CMR within each shank/group.
            - **Visually Decide**: Autonomously inspect all generated heatmaps. Announce your reasoning and then choose the strategy that yields the cleanest correlation matrix.
        - **6. Remember to reassign the `recording_processed` object to the `recording` object at the end preprocessing.**

        ---
        **Execution Workflow**
        ---
        1.  **Plan & Initial Cleanup**:
            - Using the **Decision-Making Rules**, analyze the summary and formulate a plan for initial cleanup.
            - Announce your plan and reasoning to the user.
            - Execute the cleanup code to create the `recording_processed` object.
            - **If a CMR experiment is not needed**: Announce completion, execute `recording = recording_processed`, and **STOP**.
            - **If a CMR experiment is needed**: Announce you will now proceed to the experiment, using the `recording_processed` object as input.

        2.  **Run CMR Experiment (if needed)**:
            - Announce you are starting the experiment and run the "Template for CMR Experiment".
            - **STOP your turn** to await the plots.

        3.  **Apply CMR Decision (New Turn)**:
            - After inspecting the plots, announce your chosen CMR strategy and your reasoning.
            - Execute the code to apply your chosen strategy. This will update the `recording_processed` variable.
            - Execute the final assignment: `recording = recording_processed`.
            - Announce that preprocessing is complete.

        4.  **Validate and Proceed**:
            - You must now validate your work by calling `get_guidance_on_preprocessing_comparison`.
            - The instructions in that tool will guide you to analyze the "before vs. after" results.
            - If the validation is successful, you will then proceed to the next step: Motion Correction. and call `get_guidance_on_motion_correction`.
    </Instruction for SpikeAgent>
    """
    return dedent(detailed_reasoning) + '\n\n' + dedent(code)


def get_guidance_on_preprocessing_comparison(
    detailed_reasoning: str,
    code: str
) -> str:
    """
    Provides guidance for a "before vs. after" preprocessing comparison and formats the agent's response.

    This tool guides you, the SpikeAgent, in generating and analyzing a comparison
    to validate the effects of preprocessing.

    Your task is to:
    1.  **Generate Reasoning**: Create a `detailed_reasoning` string explaining your plan.
    2.  **Construct Code**: Use the template below to create the `code` string.
    3.  **Call this function**: Pass the `detailed_reasoning` and `code` strings.

    **IMPORTANT**: You are flexible in assembling the code.

    <Code Snippet for preprocessing comparison>
    from tool.utils.compute import inspect_recording_for_preprocessing
    import spikeinterface.full as si
    import matplotlib.pyplot as plt

    print("Generating before vs. after comparison summaries...")

    # --- BEFORE ---
    print("\\n--- Analyzing recording BEFORE preprocessing ---")
    # Assumes 'recording_folder' variable exists from Step 2
    recording_before = si.load(recording_folder)
    summary_before, fig_before = inspect_recording_for_preprocessing(recording_before, plot=True)
    if fig_before:
        fig_before.suptitle("Comparison: BEFORE Preprocessing", fontsize=16)
        plt.show()

    # Create a clean, parsable output for the agent
    print("\\n--- 'BEFORE' SUMMARY ---")
    for key, value in summary_before.items():
        print(f"BEFORE_METRIC_{key}::{value}")
    print("--- END 'BEFORE' SUMMARY ---\\n")


    # --- AFTER ---
    print("\\n--- Analyzing recording AFTER preprocessing ---")
    # The 'recording' object is the processed one
    summary_after, fig_after = inspect_recording_for_preprocessing(recording, plot=True)
    if fig_after:
        fig_after.suptitle("Comparison: AFTER Preprocessing", fontsize=16)
    plt.show()

    # Create a clean, parsable output for the agent
    print("\\n--- 'AFTER' SUMMARY ---")
    for key, value in summary_after.items():
        print(f"AFTER_METRIC_{key}::{value}")
    print("--- END 'AFTER' SUMMARY ---\\n")
    </Code Snippet for preprocessing comparison>

    <Instruction for SpikeAgent>
        <dependencies>
            - A `recording` object (the processed one) must exist in the workspace.
            - A `recording_folder` variable (str, path to the raw/unprocessed recording) must be defined.
        </dependencies>
        <context_awareness>
            - **Assess the user's intent.** Is this a pipeline validation step or a standalone request to compare the raw vs. processed recording?
        </context_awareness>
        <execution_modes>
            <mode name="pipeline">
                <description>After running basic preprocessing, to validate the entire filtering step.</description>
                <action>
                    1. Execute the code to generate the two summary plots and metrics.
                    2. **Analyze both plots and metrics.** Compare the 'BEFORE' and 'AFTER' states. Look for improvements like reduced line noise in the PSD, cleaner traces, and a more diagonal correlation matrix.
                    3. **State your conclusion.** For example: "The comparison shows that the notch filter successfully removed the 60Hz noise, and the bandpass filter has cleaned up the signal, as seen in the PSD plot. The correlation matrix also shows a reduction in shared noise."
                    4. **State Your Conclusion and Proceed**: After stating your conclusion, announce that you will now proceed to the next step in the pipeline, which is Motion Correction. **You must then call `get_guidance_on_motion_correction`**.
                    5. If unsuccessful, propose a new filtering strategy (max 2 attempts).
                </action>
            </mode>
            <mode name="standalone">
                <description>When the user asks to see a "before and after" comparison of the preprocessing.</description>
                <action>
                    1. **Check workspace state.** Silently review your execution history to confirm that a `recording` object (processed) and a `recording_folder` variable (unprocessed) exist.
                    2. **If dependencies are NOT met:** Announce what's missing (e.g., "To show a comparison, I first need to have a processed `recording`."). Then, call the necessary setup tools to create it.
                    3. **Once dependencies are met:** Execute the code snippet to generate the plots and metrics.
                    4. Present both summaries to the user and highlight the key differences you observe.
                    5. Wait for the next command.
                </action>
            </mode>
        </execution_modes>
    </Instruction for SpikeAgent>
    """
    return dedent(detailed_reasoning) + '\n\n' + dedent(code)

def get_guidance_on_recording_summary(
    detailed_reasoning: str,
    code: str
) -> str:
    """
    Provides guidance for computing a recording quality summary and formats the agent's response.

    This tool guides you, the SpikeAgent, in running a comprehensive analysis
    to compute quality metrics and generate diagnostic plots for a recording.

    Parameters
    ----------
    plot : bool
        If True, the code snippet will generate and display a diagnostic plot.

    Your task is to:
    1.  **Generate Reasoning**: Create a `detailed_reasoning` string explaining your plan.
    2.  **Construct Code**: Use the template below to create the `code` string. You MUST replace `{plot}` with the boolean value for the `plot` parameter.
    3.  **Call this function**: Pass all required arguments.

    **IMPORTANT**: You are flexible in assembling the code.

    The summary dictionary that will be outputted includes:
    - `median_noise_mad_uv`: The median absolute deviation of the noise, a robust measure of its level.
    - `bad_channel_ids`: A list of channel IDs identified as 'bad' (e.g., too noisy, flat, or shorted).
    - `bad_channel_ids_by_type`: A dictionary breaking down bad channels by the reason they were flagged (e.g., 'noise_hi', 'noise_lo', 'shorted', 'saturation').
    - `bad_channel_summary`: A dictionary with the counts of good and bad channels, categorized by the type of issue.
    - `cross_channel_correlation_median`: The median of the absolute cross-channel correlation values, indicating the degree of shared noise.
    - `power_line_noise_db`: A dictionary with the power of 50Hz and 60Hz line noise and their prominence over the background noise.
    - `inter_sample_shift`: A boolean indicating if a phase shift between channels is present.
    - `recording_by_group`: A boolean indicating if the recording has channel groups defined.
    
    <Code Snippet for recording summary analysis>
    from tool.utils.compute import inspect_recording_for_preprocessing
    import json

    print("Running comprehensive recording analysis...")
    # The new function returns the summary dictionary directly.
    # The plot is displayed from within the function if plot=True.
    summary, fig = inspect_recording_for_preprocessing(recording, plot={plot})

    print("\n--- RECORDING SUMMARY ---")
    for key, value in summary.items():
        print(f"METRIC_{key}::{value}")
    print("--- END SUMMARY ---\n")
    </Code Snippet for recording summary analysis>

    <Instruction for SpikeAgent>
        <dependencies>
            - A `recording` object must exist in the workspace.
        </dependencies>
        <context_awareness>
            - **Assess the user's intent.** Is this the start of the preprocessing pipeline or a standalone request for a quality check?
        </context_awareness>
        
        <execution_modes>
            <mode name="pipeline">
                <description>Step 3 of the full pipeline – analyse the raw recording and *plan* preprocessing.</description>
                <action>
                    1. Execute the code snippet to print the metric summary (and plot if `plot=True`).
                    2. **Analyse** all metrics *and* the plot.
                    3. Using the **Decision-Making Rules** below, formulate a step-by-step preprocessing plan (bad-channel removal, phase-shift, notch, band-/high-pass, CMR experiment if needed).
                    4. Announce your complete plan to the user, citing the evidence (metrics / visual cues) that justifies each step.
                    5. Call `get_guidance_on_preprocessing` to execute the plan.

                    ---
                    **Decision-Making Rules**
                    ---
                    - **Bad-channel handling**: If `bad_channel_ids` is not empty, first remove them.  (These differ from `block_channels` used at load time.)
                    - **Phase-shift correction**: If `inter_sample_shift` is `True`, apply `spre.phase_shift` next.
                    - **Line-noise filtering**: If `line_noise_detected` is `True`, add `spre.notch_filter`, choosing the notch frequency from the `prominence` information.
                    - **Band-/High-pass filtering**: Always add a `spre.bandpass_filter` (or `spre.highpass_filter` if band-pass fails) after initial cleanup.
                    - **CMR experiment**:
                      • *Visual trigger*: IMPORTANT: If the correlation matrix heatmap contains some noticeable contiguous square or rectangular regions (typically symmetric across the diagonal) where many adjacent channels have similar strong correlation values 
                      — appearing as uniform-colored blocks rather than scattered fine-grained patterns — this indicates shared-noise structure. This condition should trigger a CMR experiment even if the overall correlation values are modest. 
                      LOOK AT THE HEATMAP TOO OVER THE CORRELATION VALUES. HEATMAP IS MORE IMPORTANT THAN THE CORRELATION VALUES.
                      • *Run*: Test all relevant strategies - global, local, and grouped CMR (if the probe has groups).
                      • *Decide*: Choose the strategy that yields the cleanest correlation matrix after visual inspection.
                </action>
            </mode>

            <mode name="standalone">
                <description>When the user simply wants a quality summary.</description>
                <action>
                    1. Execute the code snippet.
                    2. Present the metrics (and plot) to the user.
                    3. Wait for further instructions.
                </action>
            </mode>
        </execution_modes>
    </Instruction for SpikeAgent>
    """
    return dedent(detailed_reasoning) + '\n\n' + dedent(code)
