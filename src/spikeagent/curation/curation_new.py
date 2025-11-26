from textwrap import dedent
from typing import Literal


def get_guidance_on_vlm_curation(
    detailed_reasoning: str,
    code: str,
) -> str:
    """
    Provides guidance for VLM-based curation and formats the agent's response.

    This tool uses a Vision-Language Model (VLM) to classify units as "Good" or "Bad"
    based on image features and optional few-shot examples. It results in a
    `sorting_analyzer_curated` object.

    Parameters
    ----------
    model_name : str
        Name of the VLM to use (e.g., "gpt-4o", "claude_3_7_sonnet").
    features : list[str]
        List of image features to include in the prompt, available options are: ("waveform_single", "waveform_multi", "autocorr", "spike_locations", "amplitude_plot").
    good_ids : list[int]
        List of unit IDs to serve as positive few-shot examples.
    bad_ids : list[int]
        List of unit IDs to serve as negative few-shot examples.
    with_metrics : bool
        If True, include quantitative quality metrics in the prompt.
    unit_ids : list[int] | None
        List of unit IDs to curate. If None, all units will be curated.

    Your task is to:
    1.  **Generate Reasoning**: Create a `detailed_reasoning` string explaining your plan.
    2.  **Construct Code**: Use the template below, replacing placeholders with the correct values.
    3.  **Call this function**: Pass all required arguments.

    **IMPORTANT**: The code snippet below is a template. You must adapt it to the context, especially variable names. Remember that variables you define will persist across calls in the `python_repl_tool`.
    You are flexible in assembling the code. You can use parts of it, assemble new code, change the variable name based on the context, or even provide no code if the user's intent cannot be addressed by this template. Your primary goal is to fulfill the user's request effectively.

    <Code Snippet for VLM Curation>
    from spikeagent.curation.vlm_curation import run_vlm_curation, plot_spike_images_with_result
    from spikeagent.app.tool.utils import get_model
    from dotenv import load_dotenv
    from spikeagent.app.tool import si_custom as sic
    load_dotenv()
    # --- Task 1: Check for required extensions ---
    # The agent must set the `analyzer_to_curate` variable before running this.
    # analyzer_to_curate = ... # agent must set this based on the context of the conversation
    extension_map = {
        "waveform_single": "waveforms",
        "waveform_multi": "templates",
        "autocorr": "correlograms",
        "spike_locations": "spike_locations",
        "amplitude_plot": "spike_amplitudes",
    }
    features_to_run = YOUR_FEATURES_LIST # available options are: ["waveform_single", "waveform_multi", "autocorr", "spike_locations", "amplitude_plot"]
    required_extensions = set([extension_map[f] for f in features_to_run if f in extension_map])
    if YOUR_WITH_METRICS_BOOL:
        required_extensions.add("quality_metrics")

    missing_extensions = []
    for ext in required_extensions:
        if not analyzer_to_curate.has_extension(ext):
            missing_extensions.append(ext)

    if missing_extensions:
        raise ValueError(f"MISSING_EXTENSIONS::{missing_extensions}")

    print("All required extensions are available. Proceeding with VLM curation.")
    # --- Task 2: Run VLM Curation ---

    model = get_model(model_name='YOUR_MODEL_NAME_STRING') # available options are: "gpt-4o" or "claude_3_7_sonnet"
    
    # The `sorting_folder` should be defined from a previous step, but we fall back gracefully.
    if 'sorting_folder' not in globals() or sorting_folder is None:
        if analyzer_to_curate.folder:
            sorting_folder = os.path.dirname(analyzer_to_curate.folder)
        else:
            sorting_folder = os.getcwd() # Fallback to current directory
            print(f"Warning: `sorting_folder` not found. Defaulting to current directory: {sorting_folder}")

    unit_img_df = sic.create_unit_img_df(
        analyzer_to_curate,
        unit_ids=YOUR_UNIT_IDS,
        load_if_exists=False,
        save_folder=sorting_folder
    )

    results_df = run_vlm_curation(
        model=model,
        sorting_analyzer=analyzer_to_curate,
        img_df = unit_img_df,
        features=features_to_run,
        good_ids=YOUR_GOOD_IDS_LIST,
        bad_ids=YOUR_BAD_IDS_LIST,
        with_metrics=YOUR_WITH_METRICS_BOOL,
        unit_ids=YOUR_UNIT_IDS,
        num_workers=45
    )

    plot_spike_images_with_result(results_df, unit_img_df, feature="waveform_single")

    # --- Task 3: Save the reasoning and get final lists ---
    reasoning_csv_path = os.path.join(sorting_folder, 'vlm_reasoning.csv')
    results_df.to_csv(reasoning_csv_path)
    print(f"VLM reasoning log saved to: {reasoning_csv_path}")

    # The agent should parse the following outputs to understand the result and provide helper utilities.
    # ---- results_df structure & common queries ----
    #   • Index: `unit_ids`
    #   • Columns:
    #       - `average_score` (float, 0-1)
    #       - `final_classification` (str: "Good" / "Bad")
    #       - `combined_reasoning` (long text)
    #       - `reviewer_1_score`, `reviewer_1_class`, `reviewer_2_score`, `reviewer_2_class`, `reviewer_3_score`, `reviewer_3_class`
    # Example quick-checks (the agent can adapt these at run-time):
    #   results_df.loc[5]                              # full row for unit 5
    #   results_df.query("final_classification=='Good'").index.tolist()
    #   results_df.loc[5, 'combined_reasoning']        # reasoning only
    #
    # Example patterns the agent can start from (adjust as needed):
    #   • "Is unit X good?"   →  cls = results_df.loc[X, 'final_classification']
    #   • "Why was unit X labelled bad?" → reas = results_df.loc[X, 'combined_reasoning']
    #   • "What score did unit X get?"   → score = results_df.loc[X, 'average_score']
    #   • "List all bad units"           → bad_units = results_df.query("final_classification=='Bad'").index.tolist()
    # These are only guidance. The agent should adapt queries to the current context.
    # When in doubt, simply inspect the DataFrame structure, e.g. `print(results_df.head())`,
    # and build the appropriate query dynamically.
    unit_classes = results_df.groupby('final_classification').groups
    good_units = unit_classes.get('Good', []).tolist()
    bad_units = unit_classes.get('Bad', []).tolist()
    print('Final VLM Classification Results:')
    print(f"Good units: {good_units}\\nBad units: {bad_units}")

    # --- Task 4: Apply Curation ---
    # The agent must ask for user confirmation before running this part. (if in end-to-end mode, you can continue to the next step without asking the user for confirmation)
    print("\\n--- Step 4: Applying curation ---")
    if good_units:
        print(f"Applying curation and keeping {len(good_units)} units.")
        curated_analyzer = analyzer_to_curate.select_units(good_units)
        print("Created `curated_analyzer` with the good units.")
    else:
        print("No 'Good' units were found. `curated_analyzer` will be the same as the input analyzer.")
        curated_analyzer = analyzer_to_curate
    </Code Snippet for VLM Curation>
    <Instruction for SpikeAgent>
        <dependencies>
            - An input analyzer object must exist in the workspace (e.g., `sorting_analyzer`, `merged_analyzer`).
            - The analyzer must have the required extensions computed for the chosen features.
        </dependencies>
        <agent_flow_note>
            This tool supports three workflows: zero-shot, few-shot, and interactive few-shot. Your main job is to determine which workflow the user wants.
            - **Zero-shot:** No examples provided.
            - **Few-shot:** User provides `good_ids` and `bad_ids` from the start.
            - **Interactive Few-shot:** You help the user pick examples by showing them plots.
        </agent_flow_note>
        <execution_modes>
            <mode name="pipeline">
                <description>As part of the main analysis pipeline, typically the first processing step on `sorting_analyzer`.</description>
                <action>
                    1.  **Set the input analyzer.** The default input is `sorting_analyzer`. Confirm this variable exists. Set `analyzer_to_curate = sorting_analyzer`.
                    2.  **Determine Curation Workflow:**
                        - If `good_ids` or `bad_ids` were provided in the tool call, proceed directly to Step 3 (Few-Shot).
                        - If `good_ids` and `bad_ids` are both empty, **ask the user**: "No few-shot examples were provided. Would you like to run **zero-shot** curation, or shall we select some examples **interactively**?"
                            - If "zero-shot", proceed to Step 3.
                            - If "interactively", **STOP** executing this plan. Your new task is to guide the user through plotting units (using `get_guidance_on_plot_units_with_features`) and collecting their `good_ids` and `bad_ids`. Once you have them, call this curation tool again with the collected IDs.
                    3.  **Execute VLM Analysis (Tasks 1-3).**
                    4.  **Confirm with the user** before applying the result: "The VLM has classified the units. Shall I apply the curation?"
                    5.  Upon confirmation, **execute Task 4** to create `curated_analyzer`.
                    6.  Announce completion and suggest the next step.
                </action>
            </mode>
            <mode name="standalone">
                <description>When the user asks to curate an analyzer outside the standard pipeline order.</description>
                <action>
                    1.  **Silently review execution history** to see which analyzers are available (`sorting_analyzer`, `merged_analyzer`).
                    2.  **Determine the input analyzer:**
                        - If only `sorting_analyzer` exists, use it. Set `analyzer_to_curate = sorting_analyzer`.
                        - If a `merged_analyzer` also exists, the user might want to curate the result of a merge. **Ask the user for clarification**: "I see both a `sorting_analyzer` and a `merged_analyzer`. Which one would you like to curate?"
                        - Set `analyzer_to_curate` based on the user's choice.
                    3.  **Determine Curation Workflow:**
                        - If `good_ids` or `bad_ids` were provided in the tool call, proceed directly to Step 4 (Few-Shot).
                        - If `good_ids` and `bad_ids` are both empty, **ask the user**: "Would you like to run **zero-shot** curation, or shall we select some examples **interactively**?"
                            - If "zero-shot", proceed to Step 4.
                            - If "interactively", **STOP** executing this plan. Your new task is to guide the user through plotting units (using `get_guidance_on_plot_units_with_features`) and collecting their `good_ids` and `bad_ids`. Once you have them, call this curation tool again with the collected IDs.
                    4.  **Run pre-flight checks (Task 1)** and compute missing extensions.
                    5.  **Execute VLM Analysis (Tasks 2-3).**
                    6.  **Confirm with the user** before applying curation.
                    7.  Upon confirmation, **execute Task 4** to create `curated_analyzer`.
                </action>
            </mode>
        </execution_modes>
        <adaptability>
            - This tool is flexible. The agent's key responsibility is to correctly identify and set the `analyzer_to_curate` variable before execution.
            - The output is always a new object named `curated_analyzer`.
        </adaptability>
    </Instruction for SpikeAgent>
    """
    return dedent(detailed_reasoning) + '\n\n' + dedent(code)


def get_guidance_on_vlm_merge_analysis(
    detailed_reasoning: str,
    code: str,
) -> str:
    """
    Provides guidance for a VLM-based merge analysis and formats the agent's response.

    This tool finds potential merge candidates based on template similarity and then uses a VLM
    to decide which units should be merged.

    Parameters
    ----------
    model_name : str
        Name of the VLM to use, available options are "gpt-4o" or "claude_3_7_sonnet".
    features : list[str]
        Image features for the VLM's decision, available options are: ["crosscorrelograms", "amplitude_plot"].
    template_diff_thresh : float (default: 0.2)
        The similarity threshold for finding initial merge candidates.
        Note that `template_similarity = 1 - template_diff_thresh`.
        For example, a `template_diff_thresh` of 0.2 corresponds to a
        template similarity of 0.8.
    good_group_ids : list[int]
        List of group IDs (from the potential merge groups) to label as "good merges".
    bad_group_ids : list[int]
        List of group IDs (from the potential merge groups) to label as "bad merges".
        
    Your task is to:
    1.  **Generate Reasoning**: Create a `detailed_reasoning` string explaining your plan.
    2.  **Construct Code**: Use the template below, replacing placeholders with the correct values.
    3.  **Call this function**: Pass all required arguments.

    **IMPORTANT**: The code snippet below is a template. You must adapt it to the context, especially variable names. Remember that variables you define will persist across calls in the `python_repl_tool`.
    You are flexible in assembling the code. You can use parts of it, assemble new code, change the variable name based on the context, or even provide no code if the user's intent cannot be addressed by this template. Your primary goal is to fulfill the user's request effectively.

    <Code Snippet for VLM Merge Analysis>
    # --- Part 1: Compute Merge Candidates ---
    # The agent must set the `analyzer_to_merge` variable before running this.
    # Common choices are `sorting_analyzer` (for a merge-first workflow)
    # or `curated_analyzer` (for the standard curate-then-merge workflow).
    from spikeinterface.curation import compute_merge_unit_groups
    print("--- Step 1: Computing potential merge candidates ---")
    steps = ["template_similarity"]
    steps_params = {
        "template_similarity": {"template_diff_thresh": YOUR_TEMPLATE_DIFF_THRESH_FLOAT}
    }
    potential_merge_groups = compute_merge_unit_groups(
        analyzer_to_merge,
        resolve_graph=False,
        steps_params=steps_params,
        steps=steps
    )
    num_groups = len(potential_merge_groups)
    print(f"Found {num_groups} potential merge groups.")
    if num_groups > 15:
        print("Showing only the first 15 groups:")
    for i, group in enumerate(potential_merge_groups[:15]):
        print(f"  Group {i}: {group}")

    # --- Part 2: Run VLM Merge Decision ---
    import os
    from spikeagent.app.tool import si_custom as sic
    from spikeagent.curation.vlm_merge import run_vlm_merge, plot_merge_results
    from spikeagent.app.tool.utils import get_model
    from spikeinterface.curation.curation_tools import resolve_merging_graph
    if len(potential_merge_groups) == 0:
        print("NO_MERGE_CANDIDATES::No potential merge groups found. Skipping VLM merge analysis.")
        # Set the output to be the same as the input if no merges are performed
        merged_analyzer = analyzer_to_merge
    else:
        print("\n--- Step 2: Running VLM to decide on merges ---")
        model = get_model(model_name="YOUR_MODEL_NAME_STRING")
        # The `sorting_folder` should be defined from a previous step, but we fall back gracefully.
        print(f"sorting_folder: {sorting_folder}") # The agent should check if the sorting_folder is defined first before falling back to current directory
        if 'sorting_folder' not in globals() or sorting_folder is None:
            if analyzer_to_merge.folder:
                sorting_folder = os.path.dirname(analyzer_to_merge.folder)
            else:
                sorting_folder = os.getcwd() # Fallback to current directory
                print(f"Warning: `sorting_folder` not found. Defaulting to current directory: {sorting_folder}")

        merge_img_df = sic.create_merge_img_df(analyzer_to_merge, unit_groups=potential_merge_groups, load_if_exists=False, save_folder=sorting_folder)
        merge_results_df = run_vlm_merge(
            model=model,
            merge_unit_groups=potential_merge_groups,
            img_df=merge_img_df,
            features=YOUR_FEATURES_LIST, # available options are: ["crosscorrelograms", "amplitude_plot"],
            good_merge_groups=[YOUR_GOOD_GROUP_IDS_LIST], 
            bad_merge_groups=[YOUR_BAD_GROUP_IDS_LIST],
            num_workers=50
        )
        # Save CSV to deterministic path derived from analyzer
        print(f"Using sorting_folder for merge outputs: {sorting_folder}")
        merge_csv_path = os.path.join(sorting_folder,'vlm_merge_reasoning.csv')
        merge_results_df.to_csv(merge_csv_path)
        print(f"VLM merge reasoning log saved to: {merge_csv_path}")

        # The agent should parse the following outputs to understand the result and provide helper utilities.
        # ---- merge_results_df structure & common queries (VLM Merge) ----
        #   • Index: default range index
        #   • Columns:
        #       - group_id (int): The identifier for the candidate merge group.
        #       - merge_type (str): The VLM's decision, either "merge" or "not merge".
        #       - merge_units (list[int] or str): The units in the group, e.g., [0, 1]. NOTE: may be a string when read from CSV.
        #       - reasoning (str): A short, one-sentence summary of the decision.
        #       - report (str): The full, detailed report from the VLM, often multi-line.
        # Example quick-checks (the agent can adapt these at run-time):
        #   merge_results_df.head()                                # See the first few decisions
        #   merge_results_df.query("merge_type == 'merge'")        # Show only rows where merge was recommended
        #   merge_results_df.loc[0, 'reasoning']                   # Get the reasoning for the first group
        #   print(merge_results_df.loc[0, 'report'])               # Print the full VLM report for the first group
        #
        # Example patterns the agent can start from (adjust as needed):
        #   • "Which units should be merged?" → merge_pairs = merge_results_df.query("merge_type == 'merge'")['merge_units'].tolist()
        #   • "Why should units [0, 1] not be merged?" → merge_results_df.loc[merge_results_df['merge_units'].astype(str) == '[0, 1]', 'reasoning'].iloc[0]
        #
        # These are only guidance. The agent should adapt queries to the current context.
        # When in doubt, inspect the DataFrame, e.g. `print(merge_results_df.head())`.
        # NOTE: `merge_units` will be a string like '[0, 1]' if `merge_results_df` is reloaded from the CSV.
        # The agent must parse it before use, e.g., with `import ast; ast.literal_eval(string_value)`.
        merge_unit_pairs = [row.merge_units for row in merge_results_df.itertuples() if row.merge_type == "merge"]
        merge_unit_groups = resolve_merging_graph(analyzer_to_merge.sorting, merge_unit_pairs)
        print("Final Merge Decision:")
        print(merge_unit_groups)
        plot_merge_results(merge_results_df, merge_img_df)

        # --- Part 3: Apply Merges ---
        # The agent must ask for user confirmation before running this part.
        print("\n--- Step 3: Applying confirmed merges ---")
        if merge_unit_groups and len(merge_unit_groups[0]) > 0:
            print(f"Applying {len(merge_unit_groups)} merge(s): {merge_unit_groups}")
            merged_analyzer = analyzer_to_merge.merge_units(
                merge_unit_groups=merge_unit_groups,
                sparsity_overlap=0
            )
            print("Created `merged_analyzer` with merged units.")
        else:
            print("No merges to apply. `merged_analyzer` is the same as the input analyzer.")
            merged_analyzer = analyzer_to_merge
    </Code Snippet for VLM Merge Analysis>

    <Instruction for SpikeAgent>
        <dependencies>
            - An input analyzer object must exist in the workspace (e.g., `sorting_analyzer`, `curated_analyzer`).
            - The `sorting_folder` variable must be defined.
        </dependencies>
        <execution_modes>
            <mode name="pipeline">
                <description>As part of the main analysis pipeline, after curation.</description>
                <action>
                    1.  **Set the input analyzer.** The default input is `curated_analyzer`. Confirm this variable exists. Set `analyzer_to_merge = curated_analyzer`.
                    2.  Execute the code snippet to perform merge analysis, which creates `merged_analyzer`.
                    3.  Announce that the `merged_analyzer` is ready to be saved.
                </action>
            </mode>
            <mode name="standalone">
                <description>When the user asks to check for merges on an existing analyzer.</description>
                <action>
                    1.  **Silently review execution history** to see which analyzers are available (`sorting_analyzer`, `curated_analyzer`).
                    2.  **Determine the input analyzer:**
                        - If only `curated_analyzer` exists, use it. Set `analyzer_to_merge = curated_analyzer`.
                        - If only `sorting_analyzer` exists, use that for a "merge-first" workflow. Set `analyzer_to_merge = sorting_analyzer`.
                        - If both exist, the user's intent is ambiguous. **Ask for clarification**: "I see both a `sorting_analyzer` and a `curated_analyzer`. Which one would you like to check for merges?"
                        - Set `analyzer_to_merge` based on the user's choice.
                    3.  Execute the code snippet to create `merged_analyzer`.
                    4.  Present the results and ask the user if they want to save.
                </action>
            </mode>
        </execution_modes>
        <adaptability>
            - This tool is flexible. The agent's key responsibility is to correctly identify and set the `analyzer_to_merge` variable before execution.
            - The output is always a new object named `merged_analyzer`.
        </adaptability>
    </Instruction for SpikeAgent>
    """
    return dedent(detailed_reasoning) + '\n\n' + dedent(code)


def get_guidance_on_save_final_results(
    detailed_reasoning: str,
    code: str
) -> str:
    """
    Provides guidance for saving a sorting analyzer and formats the agent's response.

    This tool saves a specified analyzer object to a sub-folder within the `sorting_folder`.

    Your task is to:
    1.  **Generate Reasoning**: Create a `detailed_reasoning` string explaining your plan.
    2.  **Construct Code**: Use the template below.
    3.  **Call this function**: Pass the `detailed_reasoning` and `code` strings.

    **IMPORTANT**: The code snippet below is a template. You must adapt it to the context, especially variable names. Remember that variables you define will persist across calls in the `python_repl_tool`.
    You are flexible in assembling the code. You can use parts of it, assemble new code, change the variable name based on the context, or even provide no code if the user's intent cannot be addressed by this template. Your primary goal is to fulfill the user's request effectively.

    <Code Snippet for Saving Final Results>
    import os
    import shutil
    import spikeinterface.full as si

    # --- Task 1: Save to Disk ---
    # The agent must set the `analyzer_to_save` variable before running this.
    print("--- Saving final analyzer ---")
    saved_analyzer_path = os.path.join(sorting_folder, 'saved_sorting_analyzer.zarr')
    if os.path.exists(saved_analyzer_path):
        print(f"Removing existing folder at {saved_analyzer_path}")
        shutil.rmtree(saved_analyzer_path)

    print(f"Saving analyzer to: {saved_analyzer_path}")
    saved_analyzer = analyzer_to_save.save_as(folder=saved_analyzer_path, format='zarr')

    # --- Task 2: Verification ---
    print("--- Verifying saved analyzer ---")
    print(f"Saved object: {saved_analyzer}")
    print(f"Saved folder exists: {os.path.exists(saved_analyzer.folder)}")
    print(f"Is read-only: {saved_analyzer.is_read_only()}")
    </Code Snippet for Saving Final Results>

    <Instruction for SpikeAgent>
        <dependencies>
            - An analyzer object to save must exist in the workspace (e.g., `curated_analyzer`, `merged_analyzer`).
            - The `sorting_folder` variable must be defined.
        </dependencies>
        <execution_modes>
            <mode name="pipeline">
                <description>As the final step of the analysis pipeline.</description>
                <action>
                    1.  **Silently review execution history** to identify the most recently processed analyzer (`merged_analyzer` or `curated_analyzer`).
                    2.  **Confirm with the user.** For example: "The last step produced a `merged_analyzer`. Do you want to save this as the final result?"
                    3.  Upon confirmation, set `analyzer_to_save` to the correct variable.
                    4.  Execute the code snippet to save the chosen analyzer.
                    5.  Announce that the analysis pipeline is complete.
                </action>
            </mode>
            <mode name="standalone">
                <description>When the user wants to save a specific analyzer object.</description>
                <action>
                    1.  **Silently review execution history** to find all available analyzer objects (e.g., `curated_analyzer`, `merged_analyzer`).
                    2.  **Ask the user which analyzer to save.** Present the available options: "Which analyzer would you like to save? The available options are: `curated_analyzer`, `merged_analyzer`."
                    3.  Set `analyzer_to_save` to the user's choice.
                    4.  Execute the code snippet to save the results.
                    5.  Announce completion.
                </action>
            </mode>
        </execution_modes>
    </Instruction for SpikeAgent>
    """
    return dedent(detailed_reasoning) + '\n\n' + dedent(code)


def get_guidance_on_rigid_curation(
    detailed_reasoning: str,
    code: str
) -> str:
    """
    Provides guidance for rigid, threshold-based curation and formats the agent's response.

    This tool filters units based on signal-to-noise ratio (SNR) and inter-spike-interval
    (ISI) violation rates, creating a `curated_analyzer` object.

    Parameters
    ----------
    min_snr : float
        The minimum signal-to-noise ratio for a unit to be kept.
    max_isi : float
        The maximum ISI violation ratio (in %) for a unit to be kept.

    Your task is to:
    1.  **Generate Reasoning**: Create a `detailed_reasoning` string explaining your plan.
    2.  **Construct Code**: Use the template below, replacing placeholders with the correct values.
    3.  **Call this function**: Pass all required arguments.

    **IMPORTANT**: You are flexible in assembling the code.

    <Code Snippet for Rigid Curation>
    # --- Task 1: Check for required extensions ---
    # The agent must set the `analyzer_to_curate` variable before running this.
    if not analyzer_to_curate.has_extension('quality_metrics'):
        print("MISSING_EXTENSIONS::['quality_metrics']")
    else:
        print("All required extensions are available. Proceeding with rigid curation.")
        # --- Task 2: Run Rigid Curation ---
        print("--- Running rigid curation based on thresholds ---")
        metrics = analyzer_to_curate.get_extension('quality_metrics').get_data()
        query = f"(snr > YOUR_MIN_SNR_FLOAT) & (isi_violations_ratio < YOUR_MAX_ISI_FLOAT) & (presence_ratio > 0.9)"
        good_units = metrics.query(query).index.values
        print(f"Found {len(good_units)} good units based on query: {query}")

        curated_analyzer = analyzer_to_curate.select_units(good_units)
        print("Created `curated_analyzer` with the good units.")
    </Code Snippet for Rigid Curation>

    <Instruction for SpikeAgent>
        <dependencies>
            - An input analyzer with the 'quality_metrics' extension computed.
        </dependencies>
        <execution_modes>
            <mode name="pipeline">
                <description>As part of the main analysis pipeline, for threshold-based curation.</description>
                <action>
                    1.  **Set the input analyzer.** The default input is `sorting_analyzer`. Confirm it exists and set `analyzer_to_curate = sorting_analyzer`.
                    2.  Execute the code snippet to perform curation.
                    3.  Announce completion and suggest the next step.
                </action>
            </mode>
            <mode name="standalone">
                <description>When the user asks to run rigid, threshold-based curation directly.</description>
                <action>
                    1.  **Silently review execution history** for available analyzers (`sorting_analyzer`, `merged_analyzer`).
                    2.  **Determine the input analyzer, asking the user if ambiguous.** Set `analyzer_to_curate`.
                    3.  **Run extension checks** and compute 'quality_metrics' if missing.
                    4.  Execute the code snippet to create `curated_analyzer`.
                    5.  Present the results to the user.
                </action>
            </mode>
        </execution_modes>
    </Instruction for SpikeAgent>
    """
    return dedent(detailed_reasoning) + '\n\n' + dedent(code)
