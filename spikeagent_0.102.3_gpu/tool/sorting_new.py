from textwrap import dedent
from typing import Literal

__all__ = ["get_guidance_on_spike_sorting"]


def get_guidance_on_spike_sorting(
    detailed_reasoning: str,
    code: str
) -> str:
    """
    Provides guidance for spike sorting and formats the agent's response.

    This tool guides you through a multi-turn workflow for spike sorting and analysis.
    It covers running a sorter (like Kilosort4), creating a `SortingAnalyzer` object,
    and computing essential post-processing extensions like waveforms and quality metrics.

    Parameters
    ----------
    sorter : str
        The spike sorting algorithm to use among 'mountainsort4', 'mountainsort5', 'kilosort4', 'spykingcircus2', 'tridesclous2', 'tridesclous', 'herdingspikes'

    Your task is to:
    1.  **Generate Reasoning**: Create a `detailed_reasoning` string explaining your plan.
    2.  **Construct Code**: Use the template below to create the `code` string.
    3.  **Call this function**: Pass all required arguments.

    **IMPORTANT**: You are flexible in assembling the code. Adapt it based on your data-driven decisions and the multi-turn workflow.

    <Code Snippet for Spike Sorting and Analysis>
    import spikeinterface.full as si
    import spikeinterface.sorters as ss
    import spikeinterface.postprocessing as sp
    import spikeinterface.qualitymetrics as qm
    import spikeinterface.widgets as sw
    import os
    import matplotlib.pyplot as plt

    # This is a unified template for Steps 4 & 5. The agent must execute it in stages.

    # --- Sorting Task 1: Setup paths and check for existing results ---
    print(f"--- Starting Spike Sorting workflow with YOUR_CHOICE_OF_SORTER_NAME ---")
    sorter_name = YOUR_CHOICE_OF_SORTER_NAME
    sorting_folder = os.path.join(processed_folder, sorter_name)
    os.makedirs(sorting_folder, exist_ok=True)

    analyzer_folder = os.path.join(sorting_folder, 'sorting_analyzer.zarr') # using zarr format
    analyzer_exists = os.path.exists(analyzer_folder)

    print(f"ANALYZER_EXISTS::{analyzer_exists}")
    # --- STOP POINT 1: END OF TURN ---
    # The agent's code execution for this turn MUST end here.
    # The agent now needs to stop, parse the ANALYZER_EXISTS output,
    # and ask the user how to proceed in the NEXT turn.
    # ----------------------------------------------------

    # --- Sorting Task 2 (NEXT TURN): Load existing results OR run sorter ---
    # Based on the user's choice, you will execute ONE of the two blocks below.

    # --- Block A: Code to LOAD EXISTING SortingAnalyzer ---
    # print("Loading existing SortingAnalyzer...")
    # sorting_analyzer = si.load(analyzer_folder)
    # sorting = sorting_analyzer.sorting
    # print("SortingAnalyzer loaded successfully from previous results.")
    # ----------------------------------------------------

    # --- Block B: Code to RUN NEW sorting ---
    # print("Running a new spike sorting...")
    # default_params = ss.get_default_sorter_params(sorter_name)
    # print("Default sorter parameters:")
    # print(default_params)
    #
    # # AGENT ACTION: Ask user for parameter modifications here.
    # # For example: user_mods = {"n_jobs": -1} for parallel processing important for large datasets
    # # sorting_params = default_params.copy()
    # # sorting_params.update(user_mods)
    #
    # sorting = ss.run_sorter(
    #     sorter_name=sorter_name,
    #     recording=recording,
    #     folder=sorting_folder,
    #     remove_existing_folder=True,
    #     **sorting_params
    # )
    # print("\\n--- Sorting Result ---")
    # print(sorting)
    #
    # sorting_analyzer = si.create_sorting_analyzer(
    #     sorting=sorting,
    #     recording=recording,
    #     format='zarr',
    #     folder=analyzer_folder,
    #     overwrite=True
    # )
    # print("\\n--- SortingAnalyzer after creation ---")
    # print(sorting_analyzer)
    # print("New SortingAnalyzer created and saved successfully.")
    #
    # # --- ADDED: Verify creation of SortingAnalyzer on disk ---
    # from tool.utils.system_tools import report_directory_contents
    # print("\\n--- Verifying SortingAnalyzer creation ---")
    # report_directory_contents(path=sorting_folder, print_report=True)
    # ----------------------------------------------------
    # --- STOP POINT 2: END OF TURN ---
    # After executing EITHER Block A or Block B, the agent's turn MUST end.
    # Announce the completion of Step 4 and ask the user to proceed to Step 5.
    # ----------------------------------------------------


    # --- Sorting Task 3 (NEXT TURN): Compute extensions and quality metrics ---
    # print("\\n--- Starting Step 5: Computing analysis extensions ---")
    # job_kwargs = dict(n_jobs=8, chunk_duration="1s", progress_bar=True)
    # extension_params = {
    #     "random_spikes": {"method": "uniform", "max_spikes_per_unit": 600},
    #     "waveforms": {"ms_before": 1.0, "ms_after": 2.0},
    #     "templates": {},
    #     "template_similarity": {},
    #     "spike_locations": {"method": "grid_convolution"},
    #     "unit_locations": {},
    #     "isi_histograms": {"window_ms": 30, "bin_ms": 0.5, "method": "auto"},
    #     "correlograms": {"window_ms": 30, "bin_ms": 0.5, "method": "auto"},
    #     "spike_amplitudes": {},
    #     "noise_levels": {},
    #     "principal_components": {},
    #     "quality_metrics": {
    #         "metric_names": [
    #             "snr", "firing_rate", "isi_violation",
    #             "presence_ratio", "amplitude_cutoff", "amplitude_median", 
    #             'l_ratio', 'nearest_neighbor',
    #         ]
    #     }
    # }
    #
    # for key, value in extension_params.items():
    #     print(f"Computing {key}...")
    #     extension = sorting_analyzer.get_extension(key)
    #     if extension is None or not value.items() <= extension.params.items():
    #         sorting_analyzer.compute(key, **value, **job_kwargs)
    #     else:
    #         print(f"{key} already computed with compatible parameters")
    #
    # print("All extensions computed successfully.")
    # print("\\n--- SortingAnalyzer after extension computation ---")
    # print(sorting_analyzer)
    #
    # # Generate and save a summary plot
    # print("Generating and saving quality metrics summary plot...")
    # import tool.si_custom as sic
    # sic.plot_metrics_summary(sorting_analyzer)
    # summary_path = os.path.join(sorting_folder, 'quality_metrics_summary.png')
    # plt.savefig(summary_path)
    # plt.show()
    # print(f"Summary plot saved to: {summary_path}")

    # # --- ADDED: Verify extension creation on disk ---
    # from tool.utils.system_tools import report_directory_contents
    # print("\\n--- Verifying computed extensions in SortingAnalyzer ---")
    # report_directory_contents(path=analyzer_folder, print_report=True)
    # ----------------------------------------------------
    # --- STOP POINT 3: END OF TURN ---
    # Announce the completion of Step 5 and ask the user to proceed to Step 6.
    # ----------------------------------------------------
    </Code Snippet for Spike Sorting and Analysis>

    <Instruction for SpikeAgent>
        <dependencies>
            - A `recording` object must exist in the workspace to run a new sorting.
            - A `processed_folder` variable (str) must be defined.
        </dependencies>
        <execution_modes>
            <mode name="pipeline">
                <description>When you are at the spike sorting and analysis stage of the pipeline.</description>
                <action>
                    **IMPORTANT**: This is a multi-turn process. Follow the turn-by-turn instructions exactly.

                    **Turn 1: Check for Existing Results**
                    1.  Execute **only** `Sorting Task 1` to check if a `SortingAnalyzer` already exists.
                    2.  Parse the `ANALYZER_EXISTS::` output.
                    3.  **If results exist**, ask the user: "I found existing results for `{sorter}`. Would you like to load them, or re-run the sorter?"
                    4.  **If no results exist**, ask the user for confirmation to proceed: "I will now run the `{sorter}`. Shall I continue?"
                    5.  **STOP** and wait for the user's response.

                    **Turn 2: Load or Run Sorting**
                    1.  Based on the user's choice, execute **either** `Block A` (to load) or `Block B` (to run) from `Sorting Task 2`.
                    2.  **If running new (Block B)**, you must show the user the default parameters and ask for any modifications before executing.
                    3.  After the `sorting_analyzer` is loaded or created, announce the completion of Step 4 and ask to proceed to the analysis phase.
                    4.  **STOP** and wait for the user's response.

                    **Turn 3: Compute Extensions and Analyze**
                    1.  Execute `Sorting Task 3` to compute all analysis extensions and quality metrics.
                    2.  **Validate** that the extensions are computed and the summary plot is generated.
                    3.  Announce the completion of Step 5 and ask the user to proceed to visualization.
                </action>
            </mode>
            <mode name="standalone">
                <description>When the user asks to run a sorter or compute extensions directly.</description>
                <action>
                    1. **Check workspace state.** Silently review your execution history to confirm the necessary dependencies (`recording`, `processed_folder`) exist.
                    2. **If dependencies are NOT met:** Announce that you must load data first. Call the necessary setup tools (`get_guidance_on_environment_setup`, etc.) and get user confirmation.
                    3. **Once dependencies are met:** Proceed with the user's request, adapting the multi-turn `execution_flow` as needed. For example, you can combine turns if the user wants to run the sorter and compute extensions all at once.
                </action>
            </mode>
        </execution_modes>
        
        **IMPORTANT**: The code snippet is a template. You must adapt and execute only the relevant sections based on the turn-by-turn instructions below. Variables created in previous turns (like `recording`) are persistent and must be used correctly. Always check your execution history for the exact variable names.
        
        <execution_flow>
            <turn number="1" name="Check for Existing Results">
                <action>
                    1.  Execute **only** the `Sorting Task 1` section of the code snippet.
                    2.  Parse the `ANALYZER_EXISTS::` output to determine if previous results are available.
                </action>
                <user_interaction>
                    -   **If results exist**: Announce it to the user. Ask: "I've found existing sorting results for `{sorter}`. Would you like to load these results, or should I re-run the sorter from scratch?"
                    -   **If no results exist**: Announce this and state that you will proceed with running a new sorting. Ask: "I didn't find any previous sorting results. I will now proceed with running the `{sorter}`. Shall I continue?"
                </user_interaction>
                <completion>
                    -   **STOP and end your turn.** Wait for the user's response.
                </completion>
            </turn>

            <turn number="2" name="Load or Run Sorting">
                <action>
                    -   Based on the user's response from Turn 1, execute **either** `Block A` (to load) or `Block B` (to run) from `Sorting Task 2`.
                    -   **If running new (Block B)**: Before execution, you MUST show the user the default parameters and ask if they want to make any modifications.
                    -   **CRITICAL CHECK**: If the parameters contain `'fs'`, you MUST verify that its value matches `recording.get_sampling_frequency()`. If they do not match, you must inform the user of the mismatch and get their confirmation before proceeding.
                </action>
                <validation>
                    -   If loading existing results, confirm the `sorting_analyzer` object was loaded.
                    -   If running a new sort, confirm that the "New SortingAnalyzer created" message was printed AND that the verification directory report shows the new `sorting_analyzer.zarr` folder exists.
                </validation>
                <completion>
                    -   Call `think_and_review_before_responding` to validate the outcome.
                    -   Announce the completion of Step 4 in the standard format: "✅ Step 4 (Spike Sorting) is complete. Individual neuron spikes have been detected and clustered. Would you like me to proceed to Step 5 (Analysis) to compute quality metrics and sorting analyzer extensions?"
                    -   **STOP and end your turn.** (if in end-to-end mode, you can continue to the next step without asking the user for confirmation)
                </completion>
            </turn>

            <turn number="3" name="Compute SortingAnalyzer Extensions and Analyze">
                <action>
                    -   Execute the `Sorting Task 3` section of the code snippet to compute all the analysis extensions.
                </action>
                <validation>
                    -   Confirm that the extensions are computed successfully and that the quality metrics summary plot is generated.
                    -   Check the verification directory report to ensure that folders for the computed extensions (e.g., 'waveforms', 'quality_metrics') now exist within the `sorting_analyzer.zarr` directory.
                </validation>
                <completion>
                    -   Call `think_and_review_before_responding` to validate the outcome.
                    -   Announce the completion of Step 5: "✅ Step 5 (Analysis) is complete. Quality metrics and sorting analyzer extensions have been computed. Would you like me to proceed to Step 6 (Visualization) to plot the results for individual units? This is highly recommended to inspect the sorting quality and select potential good and bad units for VLM-based curation."
                    -   **STOP and end your turn.** (if in end-to-end mode, you can continue to the next step without asking the user for confirmation)
                </completion>
            </turn>
        </execution_flow>

        <completion_protocol>
            - **CRITICAL**: At the end of STEP 4 and STEP 5, you MUST call `think_and_review_before_responding` to validate the outcome.
            - **Validation**: Ensure the specific task for that turn (e.g., checking for results, running the sorter, computing extensions) completed successfully and without errors.
            - **End-to-End Mode**: This internal validation is MANDATORY even in end-to-end mode. You only skip asking the user for confirmation, not the internal review.
        </completion_protocol>
        
        <pro_tip>
            **How to Access Extension Data**: After computing extensions in Turn 3, the `sorting_analyzer` object is rich with data. If the user asks for specific details, you can access the data for any computed extension.
            1.  **Get the extension object**: `ext = sorting_analyzer.get_extension("extension_name")`
                -   Example: `ext_templates = sorting_analyzer.get_extension("templates")`
            2.  **Get the data from the extension**: `data = ext.get_data()`
                -   Some extensions have options. For "templates", you can get the average or median.
                -   Example: `avg_templates = ext_templates.get_data(operator="average")`
                -   Example: `median_templates = ext_templates.get_data(operator="median")`
            3.  **To see what an extension can do**, use the `help()` function: such as `help(ext_templates)`, `help(ext_waveforms)`, `help(ext_isi_histograms)`, etc. in python_repl_tool to see the documentation of the specific extension.
            4.  **Accessing Quality Metrics**: Quality metrics are a special case and are returned as a pandas DataFrame, which is very useful for analysis.
                -   `qm_df = sorting_analyzer.get_extension("quality_metrics").get_data()`
                -   `print(qm_df.head())`
        </pro_tip>
    </Instruction for SpikeAgent>
    """
    return dedent(detailed_reasoning) + '\n\n' + dedent(code) 