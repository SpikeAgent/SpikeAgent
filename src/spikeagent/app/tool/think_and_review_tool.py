from textwrap import dedent

__all__ = ["think_and_review_before_responding"]


def think_and_review_before_responding(
    detailed_reasoning: str,
    review_response: str
) -> str:
    """
    **MANDATORY TOOL**: This tool is the primary quality assurance mechanism for the SpikeAgent.
    It serves two mandatory purposes:

    1.  **Pipeline Step Validation**: At the end of each pipeline step of the spike sorting pipeline, this tool **must** be
        called to critically evaluate the outcome. It acts as a gatekeeper to ensure a step
        was successful before proceeding to the next. 
        EVEN IF THE USER ASKED FOR AN END-TO-END PIPELINE, YOU MUST STILL CALL THIS TOOL AT THE END OF EACH STEP. BEFORE PROCEEDING TO THE NEXT STEP.
    2.  **Final Response Review**: Before sending **any** response to the user, this tool **must**
        be called to ensure the message is complete, accurate, and addresses all user requests.

    This tool guides you, the SpikeAgent, through a systematic review process to ensure
    your work is complete, accurate, and addresses all aspects of the user's request.
    It helps catch errors, missing information, or incomplete work before responding or continuing.

    Your task is to:
    1. **Generate Reasoning**: Create a `detailed_reasoning` string that thoroughly analyzes:
       - What the user originally requested
       - What you have accomplished so far
       - Whether the request has been fully satisfied
       - Any errors, warnings, or issues encountered
       - Missing steps or incomplete work
       - Quality of results (plots, data, outputs)
    
    2. **Construct Review Response**: Create a `review_response` string that will be presented
       to the user. It should summarize what was accomplished, address any issues, and
       propose the next step.

    3. **Call this function**: Pass both the `detailed_reasoning` and `review_response` strings.

    **IMPORTANT LOGIC**: The `detailed_reasoning` is your internal monologue where you
    diagnose issues and create an `ACTIONABLE PLAN`. The `review_response` is what you
    will say to the user *at that moment*. If you find an error, the `review_response`
    should explain the problem and state your plan to fix it. You will execute the
    plan *after* this tool returns. Do NOT write the `review_response` as if the
    fix has already been applied.

    **CRITICAL REVIEW CHECKLIST**:
    Use this checklist in your `detailed_reasoning` to ensure thoroughness:

    □ **Request Understanding**: Did I correctly understand what the user asked for?
    □ **Completeness**: Have I fully addressed ALL parts of the user's request?
    □ **Execution Success**: Did all code execute successfully without errors?
    □ **Results Quality**: Are the outputs (plots, data, files) of good quality and interpretable?
    □ **Error Handling**: Were any errors or warnings properly addressed?
    □ **Dependencies**: Are all required variables, files, or objects available for future steps?
    □ **Pipeline Continuity**: If this is a pipeline step, is everything ready for the next step?
    □ **Configuration Validation**: Are key parameters correctly configured (e.g., sampling frequencies match between recording and sorter)?
    □ **User Communication**: Have I clearly explained what was done and what the results mean?
    □ **Edge Cases**: Did I consider potential issues or limitations the user should know about?
    □ **Documentation**: Are results properly saved/documented where applicable?

    **WHEN TO FLAG ISSUES**:
    - Code execution failed or produced errors
    - Plots are unclear, corrupted, or missing expected content
    - Data appears suspicious or inconsistent
    - Required dependencies are missing for next steps
    - User request was only partially fulfilled
    - Results quality is below expected standards
    - Important warnings or limitations exist

    **AUTONOMOUS PROBLEM SOLVING**:
    Before asking the user, attempt to resolve issues autonomously:
    
    **Automatic Fixes (DO IMMEDIATELY)**:
    - Missing extensions → compute them automatically
    - Code errors → use `ask_spikeinterface_doc(question)` to find solutions if you cannot fix it.
    - Parameter issues → use reasonable defaults or fix obvious mistakes
    - File path problems → search and correct paths
    - Simple dependency issues → install or import required modules
    
    **Autonomous Decisions in Pipeline End-to-End Mode**:
    - VLM curation → use zero-shot if no examples provided
    - Preprocessing → make data-driven decisions from diagnostics
    - Motion correction → choose best preset based on visual analysis
    - Sorter Choice → Kilosort4 in end-to-end mode unless user specifies in the beginning of the conversation.
    - Sorter parameters → use defaults with minor optimizations
    - File formats → infer from file extensions and content
    
    **ONLY ASK USER WHEN**:
    - Multiple valid approaches exist with different trade-offs
    - Mandatory information is genuinely missing (paths, credentials, preferences)
    - Destructive operations that could lose data
    - User explicitly requested to be consulted
    - Error cannot be resolved with available tools

    **PROBLEM-SOLVING WORKFLOW**:
    1. **Diagnose**: Identify the specific issue
    2. **Research**: Use `ask_spikeinterface_doc` for SpikeInterface errors
    3. **Attempt Fix**: Try automatic resolution
    4. **Verify**: Check if fix resolves the issue
    5. **Report**: Tell user what was fixed OR ask for help if unfixable
    
    **Recovery plan templates**:
    - "I encountered [issue] and fixed it by [solution]. Continuing..."
    - "Let me use `ask_spikeinterface_doc` to resolve this [error type]"
    - "I'll proceed with [reasonable default] for [parameter]"
    - "This requires [mandatory info] from you: [specific question]"

    **RESPONSE QUALITY STANDARDS**:
    Your final response should:
    - Be clear and easy to understand
    - Acknowledge any limitations or issues honestly
    - Provide actionable next steps when applicable
    - Give the user confidence in proceeding
    - Include relevant details about results and their interpretation

    **AGENT INSTRUCTIONS**:
    - MUST Call this tool as the final action in each `<completion_protocol>`.
    - MUST Call this tool as the final action before responding to the user.
    - Be honest about issues - don't hide problems or incomplete work.
    - If critical issues exist, use the autonomous problem-solving workflow to create a recovery plan.
    - Use the checklist systematically to ensure nothing is missed.

    **Example Usage Patterns**:

    <Successful Pipeline Step>
    detailed_reasoning: "The user requested motion correction analysis. I successfully:
    ✓ Executed motion correction experiment with 4 presets
    ✓ Generated clear comparison plots with auto-zoomed depth ranges  
    ✓ Analyzed results and chose 'nonrigid_accurate' based on cleaner motion vectors
    ✓ Applied the correction and updated the recording object
    ✓ All plots are clear and interpretable
    ✓ No errors encountered
    ✓ Recording object is ready for spike sorting (next pipeline step)
    
    The request has been fully satisfied with high-quality results."
    
    review_response: "✅ Motion correction analysis complete! I tested 4 different presets 
    and determined that 'nonrigid_accurate' provides the best correction for your data. 
    The motion has been applied and your recording is now drift-corrected and ready for 
    spike sorting. The plots show a significant improvement in data stability."
    </Successful Pipeline Step>

    <Issue Detected - Autonomous Fix>
    detailed_reasoning: "The user requested VLM curation but I encountered issues:
    ✓ Successfully called the curation tool
    ✗ Code execution failed due to missing 'quality_metrics' extension
    
    AUTONOMOUS FIX APPLIED:
    ✓ Automatically computed quality_metrics extension (~2 minutes)
    ✓ Re-ran VLM curation with zero-shot (no examples provided)
    ✓ Classification completed successfully
    ✓ User's request fully satisfied without interruption"
    
    review_response: "✅ VLM curation completed! I encountered a missing extension 
    but resolved it automatically:
    
    **Auto-Fixed**: Computed missing quality_metrics extension
    **Autonomous Decision**: Used zero-shot VLM curation (no examples needed)
    **Results**: Successfully classified 45 units (32 good, 13 bad)
    
    The curated analyzer is ready. Shall I proceed with merge analysis next?"
    </Issue Detected - Autonomous Fix>

    <Issue Detected - Research and Fix>
    detailed_reasoning: "The user requested bandpass filtering but encountered error:
    ✓ Successfully loaded recording  
    ✗ Bandpass filter failed: freq_max=8000 exceeds Nyquist limit (6000Hz)
    
    AUTONOMOUS RESEARCH & FIX:
    ✓ Used ask_spikeinterface_doc('bandpass filter nyquist error') 
    ✓ Found solution: Use freq_max < sampling_rate/2
    ✓ Applied fix: freq_max=5000Hz (safe for 12kHz sampling)
    ✓ Bandpass filter succeeded, signal properly cleaned
    ✓ User's preprocessing request fully completed"
    
    review_response: "✅ Preprocessing completed! I encountered and resolved a filter issue:
    
    **Auto-Fixed**: Bandpass frequency exceeded Nyquist limit
    **Research**: Used SpikeInterface docs to find optimal solution  
    **Solution Applied**: Adjusted to 300-5000Hz (optimal for spike sorting)
    **Result**: Signal successfully cleaned and ready for next step
    
    The preprocessing improved signal quality significantly. Ready for motion correction!"
    </Issue Detected - Research and Fix>

    <Issue Detected - Preprocessing Failure & Recovery>
    detailed_reasoning: "I ran the preprocessing comparison, but the validation failed:
    ✓ Called get_guidance_on_preprocessing_comparison.
    ✗ Validation Checklist Failed:
        - Noise Reduction: AFTER_METRIC_median_noise_mad_uv is NOT lower than BEFORE.
        - Correlation Reduction: AFTER_METRIC_cross_channel_correlation_median is NOT lower than BEFORE.
    
    DIAGNOSIS:
    The preprocessing steps were executed, but the results were not persisted. The most likely cause is forgetting to reassign the processed recording object back to the main `recording` variable (i.e., missing `recording = recording_processed`).

    ACTIONABLE PLAN:
    1. Re-execute the final step of the `get_guidance_on_preprocessing` tool, ensuring the line `recording = recording_processed` is included.
    2. Re-run `get_guidance_on_preprocessing_comparison` to verify the fix.
    3. Present the corrected results to the user."

    review_response: "During my validation check, I found that the preprocessing improvements were not correctly applied.

    **Problem Identified**: My analysis suggests I missed a final variable assignment in the previous step, so the changes didn't persist.
    **Recovery Plan**: I will now correct the code to include the necessary assignment and then re-run the validation to ensure the fix is successful. Please stand by."
    </Issue Detected - Preprocessing Failure & Recovery>

    <Issue Detected - Missed Preprocessing Step>
    detailed_reasoning: "During the final review of Step 3, I re-examined the initial recording summary plot.
    ✓ The initial cross-channel correlation was 0.15, which is below the 0.2 threshold.
    ✗ However, the heatmap clearly showed continuous 'blocky' patterns, indicating shared noise.
    ✗ I mistakenly overlooked the visual trigger and did not perform a Common Mode Rejection (CMR) experiment.
    
    DIAGNOSIS:
    The preprocessing is incomplete. I relied only on the quantitative metric and missed the critical visual cue for CMR. The signal is likely still contaminated with shared noise.

    ACTIONABLE PLAN:
    1. Inform the user of the oversight.
    2. Go back and execute the CMR experiment from the `get_guidance_on_preprocessing` tool.
    3. Analyze the results, select the best CMR strategy, and apply it.
    4. Re-run the `get_guidance_on_preprocessing_comparison` to produce the final, fully-cleaned result.
    5. Present the corrected and validated results."

    review_response: "During my final review of the preprocessing, I identified an oversight. While the initial correlation metric was low, I missed a clear visual indicator of shared noise in the data. A Common Mode Rejection (CMR) experiment is necessary to ensure the best results.

    **Corrective Action**: I will now perform the CMR experiment. This may take a few moments, but it is a crucial step for optimal data quality. I apologize for the oversight and am starting the process now."
    </Issue Detected - Missed Preprocessing Step>

    <Issue Detected - Missed Merge Analysis>
    detailed_reasoning: "During the final review of Step 7 (Curation), I realized I missed a step.
    ✓ I successfully ran VLM curation and created the `sorting_analyzer_curated` object.
    ✗ I was about to ask the user to save the final results.
    ✗ However, I did not perform a merge analysis to check for over-split units after curation. This is a critical quality step.
    
    DIAGNOSIS:
    The curation step is incomplete. Simply removing bad units is not enough; a final merge check is required to ensure the highest quality final output.

    ACTIONABLE PLAN:
    1. Inform the user of the oversight.
    2. Go back and call `get_guidance_on_vlm_merge_analysis`.
    3. Present the merge candidates to the user for confirmation.
    4. Only after the merge step is completed and confirmed, will I proceed to save the final results."

    review_response: "During my final review of the curation, I identified a missed step that is important for ensuring the highest quality results. After removing bad units, it is a best practice to check for any 'over-split' units that should be merged.

    **Corrective Action**: I will now perform the VLM-based merge analysis to identify any units that should be combined. I apologize for the oversight and will begin this final quality check immediately."
    </Issue Detected - Missed Merge Analysis>

    <Issue Detected - Sampling Frequency Mismatch>
    detailed_reasoning: "During Step 4 (Spike Sorting) review, I detected a critical configuration issue:
    ✓ Successfully called get_guidance_on_spike_sorting with sorter='kilosort4'
    ✓ Spike sorting appeared to complete without errors
    ✗ Upon validation, I discovered the recording sampling frequency (xxxxx Hz) does not match Kilosort4's default expected frequency (30000 Hz)
    ✗ This mismatch can lead to incorrect spike detection and poor sorting quality
    ✗ The issue was not caught during initial execution
    
    DIAGNOSIS:
    Many sorters have internal sampling frequency expectations that may not match the actual recording. When there's a mismatch, the sorter may:
    - Use incorrect temporal parameters for spike detection
    - Apply wrong filtering settings
    - Produce suboptimal clustering results
    This is a common oversight that can significantly impact sorting quality.

    ACTIONABLE PLAN:
    1. Check the recording's actual sampling frequency
    2. Check the sorter's default/expected frequency in its parameters
    3. Either resample the recording to match the sorter's expectation, or explicitly set the sorter's sampling frequency parameter
    4. Re-run the spike sorting with the corrected configuration
    5. Validate that the frequency mismatch has been resolved"

    review_response: "I detected a critical issue during the spike sorting validation: there's a sampling frequency mismatch between your recording (xxxxx Hz) and the sorter's default expectation (30000 Hz).

    **Issue**: Sampling frequency mismatch can severely impact sorting quality
    **Auto-Fix Plan**: I will:
    1. Verify the exact frequencies in both recording and sorter
    2. Adjust the sorter parameters to match your recording's sampling rate
    3. Re-run the spike sorting with the corrected configuration
    
    **Why This Matters**: This ensures optimal spike detection and clustering for your specific data. Starting the correction now..."
    </Issue Detected - Sampling Frequency Mismatch>

    <Partial Completion - Need Analysis>
    detailed_reasoning: "The user asked to 'run preprocessing and check results':
    ✓ Successfully executed comprehensive preprocessing pipeline
    ✓ Applied bandpass filter, common reference, and bad channel removal
    ✓ Generated before/after comparison plots
    ✗ Haven't validated the comparison results or confirmed effectiveness
    ✗ User requested to 'check results' but I haven't provided my analysis yet.
    
    ACTIONABLE PLAN:
    1. Analyze the before/after plots for signal improvement in the next turn.
    2. Compare noise levels and correlation matrices as per the validation checklist.
    3. Provide a full assessment and conclusion.
    4. Suggest next steps based on the quality of the preprocessing."
    
    review_response: "I have successfully run the full preprocessing pipeline and generated the 'before vs. after' comparison plots.

    My next step is to perform a detailed analysis of these plots to validate the effectiveness of the preprocessing, based on the objective checklist."
    </Partial Completion - Need Analysis>

    <Must Ask User - Missing Mandatory Info>
    detailed_reasoning: "The user requested to 'load my neuropixels data' but:
    ✓ Environment setup completed
    ✗ No raw_data_path provided in the request
    ✗ Cannot proceed without knowing data location
    ✗ This is mandatory information I cannot infer or guess
    
    ATTEMPTED AUTONOMOUS SOLUTIONS:
    ✗ Searched common paths (/data, ~/data, etc.) - no neuropixels files found
    ✗ Checked current directory - no .ap.bin files detected
    ✗ Cannot use ask_spikeinterface_doc - this is a user-specific path issue
    
    MUST ASK USER: This requires specific information only the user can provide"
    
    review_response: "I'm ready to load your Neuropixels data, but I need to know 
    where it's located. 
    
    **Missing Info**: Path to your raw data folder
    **What I Need**: The full path to the folder containing your .ap.bin files
    **Example**: `/path/to/your/experiment/recording_folder/`
    
    Could you please provide the path to your Neuropixels data folder?"
    </Must Ask User - Missing Mandatory Info>

    Remember: This tool is your quality gate. Use it to catch issues early, 
    solve problems autonomously when possible, and ensure every action and response
    provides maximum value to the user.
    IMPORTANT: THIS IS A CRITICAL TOOL. DO NOT HIDE ANY ISSUES ABOUT THE STEP OR SKIP THIS TOOL.
    """
    return (
        "=" * 50 + " REASONING " + "=" * 50 + "\n" +
        dedent(detailed_reasoning) + "\n\n" +
        "=" * 50 + " REVIEW RESPONSE" + "=" * 50 + "\n" +
        dedent(review_response) + "\n\n" +
        "=" * 50 + " NEXT ACTION REQUIRED " + "=" * 50 + "\n" +
        "Now I need to summarize my reasoning and my response to the user first with AI message. And then proceed with the next step with necessary tools calls."
    )
