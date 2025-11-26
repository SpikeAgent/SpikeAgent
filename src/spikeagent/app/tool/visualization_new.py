from textwrap import dedent

__all__ = ["get_guidance_on_plot_units_with_features"]


def get_guidance_on_plot_units_with_features(
    detailed_reasoning: str,
    code: str,
) -> str:
    """
    Provides guidance for plotting unit features and formats the agent's response.

    This tool guides you, the SpikeAgent, in plotting various feature images for
    specified units from a SortingAnalyzer, such as waveforms and spike locations.

    Parameters
    ----------
    features : list[str]
        List of features to plot, available options are: ["waveform_single", "waveform_multi", "autocorr", "spike_locations", "amplitude_plot"].
    unit_ids : list[int] | None
        Unit IDs to plot. If None, the first 10 units are plotted by default. Default to None in end-to-end mode.
    save : bool
        If True, images are saved to ``<analyzer.folder>/feature_plot``.

    Your task is to:
    1.  **Generate Reasoning**: Create a `detailed_reasoning` string explaining your plan.
    2.  **Construct Code**: Use the template below to create the `code` string. You MUST replace
        the placeholders for `features`, `unit_ids`, and `save` with the correct values.
    3.  **Call this function**: Pass all required arguments.

    **IMPORTANT**: The code snippet below is a template. You must adapt it to the context, especially variable names. Remember that variables you define will persist across calls in the `python_repl_tool`.
    You are flexible in assembling the code. You can use parts of it, assemble new code, change the variable name based on the context, or even provide no code if the user's intent cannot be addressed by this template. Your primary goal is to fulfill the user's request effectively.

    <Code Snippet for plotting unit feature images>
    # Agent Action: You must first decide which SortingAnalyzer to use.
    # If a curated analyzer (e.g., `sorting_analyzer_curated`) exists,
    # it should be used. Otherwise, use the original `sorting_analyzer`.
    #
    # Available features for the 'features' parameter:
    # "waveform_single", "waveform_multi", "autocorr", "spike_locations", "amplitude_plot"
    from spikeagent.app.tool import si_custom as sic

    # --- Task 1: Check for required extensions ---
    # Set the correct analyzer object here based on your assessment of the context.
    analyzer_to_use = sorting_analyzer  # Or `sorting_analyzer_curated` if it exists

    # Define which extensions are needed for the requested features
    extension_map = {
        "waveform_single": "templates",
        "waveform_multi": "templates",
        "autocorr": "correlograms",
        "spike_locations": "spike_locations",
        "amplitude_plot": "spike_amplitudes",
    }
    features_to_plot = YOUR_FEATURES_LIST # e.g., ["waveform_single", "autocorr"]
    # Will throw out an error if you try to plot a feature that is not supported.
    required_extensions = set([extension_map[f] for f in features_to_plot if f in extension_map])

    missing_extensions = []
    for ext in required_extensions:
        if not analyzer_to_use.has_extension(ext):
            missing_extensions.append(ext)

    if missing_extensions:
        print(f"MISSING_EXTENSIONS::{missing_extensions}")
    else:
        print("All required extensions are available.")
        # --- Task 2: Plot the features ---
        units_to_plot = YOUR_UNIT_IDS # e.g., [1, 2, 3] or None, you can set to None in end-to-end mode, which will plot the first 10 units by default.

        sic.plot_units_with_features(
            analyzer_to_use,
            unit_ids=units_to_plot,
            features=features_to_plot,
            save=YOUR_SAVE_BOOLEAN, # e.g., True or False
        )
    </Code Snippet for plotting unit feature images>

    <Instruction for SpikeAgent>
        <dependencies>
            - A `sorting_analyzer` object must exist in the workspace.
            - The analyzer must have the required extensions computed (e.g., 'waveforms', 'spike_amplitudes').
        </dependencies>
        <execution_modes>
            <mode name="pipeline">
                <description>As part of the main analysis pipeline (Step 6), to visualize unit properties.</description>
                <action>
                    1.  **Execute**: Run Task 1 to check extensions, then run Task 2 to plot the features.
                    2.  **Confirm with User**: Announce Step 6 completion and ask to proceed to Step 7 (Curation). 
                </action>
            </mode>
            <mode name="standalone">
                <description>When the user asks to plot specific features for one or more units.</description>
                <action>
                    1.  **Check for `sorting_analyzer`.** Review your history to see if an analyzer is loaded. If not, announce it and use `get_guidance_on_environment_setup` to find and load one.
                    2.  **Once an analyzer is loaded, run the extension check (Task 1).**
                    3.  **If `MISSING_EXTENSIONS` is printed:**
                        - Announce which extensions are missing (e.g., "To plot waveforms, I first need to compute them.").
                        - Get the code from `Sorting Task 3` in `get_guidance_on_spike_sorting`.
                        - Adapt that code to compute *only the missing extensions*.
                        - Execute the code to compute them.
                    4.  **Once all extensions are available, execute the plotting code (Task 2).**
                    5.  Present the plot to the user and wait for the next command.
                </action>
            </mode>
        </execution_modes>
    </Instruction for SpikeAgent>
    """
    return dedent(detailed_reasoning) + '\n\n' + dedent(code)
