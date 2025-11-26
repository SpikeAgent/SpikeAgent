# tool/start.py
from textwrap import dedent

__all__ = ["get_guidance_on_environment_setup"]

def get_guidance_on_environment_setup(
    detailed_reasoning: str,
    code: str
) -> str:
    """
    This function formats the `detailed_reasoning` and `code` that you, the SpikeAgent, provide.

    Parameters
    ----------
    save_path : str
        The root path where processed data and results will be saved.
    raw_data_path : str
        The path to the raw experimental data.

    Your task is to:
    1.  **Generate Reasoning**: Create a `detailed_reasoning` string that explains your plan for setting up the environment based on the user's request.
    2.  **Construct Code**: Use the `<Code Snippet for Environment Setup and Investigation>` template below to create the `code` string. You MUST replace `"{save_path}"` and `"{raw_data_path}"` with the actual values provided to this function.
    3.  **Call this function**: Pass the `save_path`, `raw_data_path`, and the `detailed_reasoning` and `code` strings you just created as arguments.

    The function will then return the combined, formatted output for you to use.

    **IMPORTANT**: The code snippet below is a template. You must adapt it to the context, especially variable names. Remember that variables you define will persist across calls in the `python_repl_tool`.
    You are flexible in assembling the code. You can use parts of it, assemble new code, change the variable name based on the context, or even provide no code if the user's intent cannot be addressed by this template. Your primary goal is to fulfill the user's request effectively.
    
    <Code Snippet for Environment Setup and Investigation>
import os
import spikeinterface.full as si
# We assume the agent has access to this new utility
from spikeagent.app.tool.utils.system_tools import report_directory_contents
# Set global job kwargs to -1
si.set_global_job_kwargs(n_jobs=-1)

# --- 1. Set up paths and create folders ---
save_path = "{save_path}"
raw_data_path = "{raw_data_path}"

if not os.path.exists(raw_data_path):
    print(f"Error: The raw_data_path does not exist: {raw_data_path}")
else:
    raw_folder_name = os.path.basename(raw_data_path)
    processed_folder = os.path.join(save_path, raw_folder_name)
    os.makedirs(processed_folder, exist_ok=True)
    print(f"Project folder is set to: {processed_folder}")

    # --- 2. Report on the contents of the directories ---
    print("\\n--- Processed Folder Status ---")
    report_directory_contents(path=processed_folder, print_report=True)

    print("\\n--- Raw Data Folder Status ---")
    report_directory_contents(path=raw_data_path, print_report=True)

    # --- 3. Final check for key objects ---
    recording_folder = os.path.join(processed_folder, 'recording')
    # The agent should find the sorter and analyzer folders dynamically
    print(f"\\nConclusion: Use the report above to check for 'recording' or 'sorting_analyzer' folders.")

    # --- Task 2 (Optional): Code example to load an existing SortingAnalyzer ---
    # If the user chooses to load, the agent can uncomment and execute this block.
    #
    # print("\\n--- Loading existing SortingAnalyzer ---")
    # # INSTRUCTION FOR AGENT:
    # # You must construct the full path to the `sorting_analyzer` folder here.
    # # Use the `processed_folder` variable and combine it with the path you
    # # identified from the "Processed Folder Status" report.
    # analyzer_folder = "..." # E.g., os.path.join(processed_folder, 'kilosort4', 'sorting_analyzer.zarr')
    # sorting_analyzer = si.load_sorting_analyzer(analyzer_folder)
    # print("SortingAnalyzer loaded successfully.")
    # print(sorting_analyzer)
    # -----------------------------------------------------------------


</Code Snippet for Environment Setup and Investigation>

<Instruction for SpikeAgent>
    <dependencies>
        - User-provided `save_path` and `raw_data_path`.
    </dependencies>
    <execution_modes>
        <mode name="pipeline">
            <description>
As the first step of the analysis pipeline, to set up the workspace and create a full plan based on the file structure.
It uses a Python function to find key objects and `report_directory_contents` to list raw files.

**Expected Folder Structure**: The `processed_folder` may contain sub-folders for each sorter (e.g., 'kilosort4'), which in turn contain the `sorting_analyzer.zarr`. A preprocessed `recording` is typically saved at the root of the `processed_folder` as `processed_folder/recording`.
            </description>
            <action>
                **IMPORTANT**: The code snippets are templates. You must adapt them to the context. Variables you create (like `processed_folder`) persist across turns.

                1.  **Execute Code**: Use `python_repl_tool` to execute the code snippet.
                2.  **Parse JSON**: Parse the `ANALYSIS_RESULTS` JSON output to get a structured list of found `recording` and `analyzers`.
                3.  **Analyze and Decide**:
                    - **If analyzers are found**: Prioritize them (`processed` > `base`). Announce all findings, highlighting the most processed one. Propose these options to the user, starting with the best:
                        1. Load the most processed analyzer (e.g., `sorting_curated.zarr`) to jump to **visualization (Step 6)** or **curation (Step 7)**.
                        2. Load an intermediate analyzer.
                        3. Load the preprocessed `recording` (if available).
                        4. Start the entire pipeline from scratch from raw data.
                        **WAIT** for the user's choice before proceeding.
                    - **If only a `recording` is found**: Announce the finding. Your next action is to call `get_guidance_on_loading_recording`.
                    - **If nothing is found**: Proceed to analyze the "Raw Data Folder Status" report to load from raw data.
                4.  **Raw Data Loading Plan**:
                    - If you must load from raw data, examine the filenames in the "Raw Data Folder Status" report to infer the `data_format`.
                    - **Use these rules for inference**:
                        - If you see `binary.json` or `recording.json` alongside `traces_cached_seg0.raw`, the format is **"spikeinterface_binary"**.
                        - If you see `.ap.bin` and `.ap.meta` files, the format is **"neuropixels"**.
                        - If you see `.rhd` files, the format is **"intan_rhd"**.
                        - If ambiguous, **ask the user** for the data format.
                    - Your next action is to call `get_guidance_on_loading_raw_data` with the correct format.
                5.  **Confirm with User**: After presenting your findings and plan, if not in end-to-end mode, you must ask the standard Step 1 completion question ("✅ Step 1… proceed to Step 2?") and wait for permission.
            </action>
        </mode>
    </execution_modes>
</Instruction for SpikeAgent>

    """
    return dedent(detailed_reasoning) + '\n\n' + dedent(code)