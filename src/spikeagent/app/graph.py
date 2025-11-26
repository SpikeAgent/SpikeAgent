import os
import json
import streamlit as st

#from langchain_experimental.utilities.python import PythonREPL
from spikeagent.app.tool.utils.python_repl_tool import PythonREPL
from langchain_core.messages import HumanMessage, BaseMessage, ToolMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.config import RunnableConfig
from langchain_core.tools import tool

from spikeagent.app.tool.utils.custom_class import ChatAnthropic_H
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_google_genai import ChatGoogleGenerativeAI

from langgraph.graph import START, StateGraph
from langgraph.graph.message import AnyMessage, add_messages
from langgraph.prebuilt import ToolNode
from langgraph.types import Command

from spikeagent.app.st_utils.comp_img import compress_and_encode
from spikeagent.app.st_utils.st_display import render_conversation_history

from typing import Annotated, TypedDict, Literal, Tuple, List
from pydantic import BaseModel, Field
from datetime import datetime
import matplotlib.pyplot as plt

from dotenv import load_dotenv
load_dotenv()

from spikeagent.app.tool.utils import get_model

# Directory Setup
tmp_folder = "tmp/plots"
os.makedirs(tmp_folder, exist_ok=True)

class GraphsState(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]
    input_messages_len: list[int]



class Graph_generator():
    def __init__(self, selected_model, tools):
        self.model_name = selected_model

        model = get_model(selected_model, temperature=0.7)
        llm_chain = model.bind_tools(tools)

        tool_node = ToolNode(tools)
        call_node = make_call_node(llm_chain)

        graph = StateGraph(GraphsState)
        graph.add_edge(START, "call")
        graph.add_node("tools", tool_node)
        graph.add_node("call", call_node)
        graph.add_edge("tools", "call")
        self.graph_runnable = graph.compile()

    def invoke_our_graph(self, messages):
        config = {"recursion_limit": 200, "configurable": {"model_name": self.model_name}}
        return self.graph_runnable.invoke({"messages": messages, "input_messages_len": [len(messages)]}, config=config)



def make_call_node(llm):
    def _call_model(state: GraphsState, config: RunnableConfig) -> Command[Literal["tools", "__end__"]]:
        model_name = config["configurable"].get("model_name", "gpt-4o")

        st.session_state["final_state"]["messages"] = state["messages"]
        previous_message_count = len(state["messages"])
        state["input_messages_len"].append(previous_message_count)
        render_conversation_history(state["messages"][state["input_messages_len"][-2]:state["input_messages_len"][-1]])
        cur_messages_len = len(state["messages"]) - state["input_messages_len"][0]

        if cur_messages_len > 200:
            st.markdown(
                f"""
                <p style="color:blue; font-size:16px;">
                    Current recursion step is {cur_messages_len}. Terminated because you exceeded the limit of 50.
                </p>
                """,
                unsafe_allow_html=True
            )
            st.session_state["render_last_message"] = False
            return Command(
                update={"messages": []},
                goto="__end__",
            )

        last_message = state["messages"][-1]
        if isinstance(last_message, ToolMessage) and last_message.name == 'python_repl_tool':
            content_list = []
            if hasattr(last_message, 'artifact') and last_message.artifact and model_name != "gpt-3.5-turbo":
                for rel_path in last_message.artifact:
                    if rel_path.endswith(".png"):
                        abs_path = os.path.join(os.path.dirname(__file__), rel_path)
                        if os.path.exists(abs_path):
                            with open(abs_path, "rb") as image_file:
                                image_data = compress_and_encode(image_file)
                            content_list.append({
                                "type": "image_url",
                                "image_url": {"url": f"data:image/png;base64,{image_data}"}
                            })

                if hasattr(last_message, 'content') and "$_$" in last_message.content:
                    if "Recording Comparison" in last_message.content: 
                        print('--------------------------------------------')
                        import os
                        _app_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                        filter_ref_path = os.path.join(_app_dir, "app", "st_utils", "filter_ref.png")
                        with open(filter_ref_path, "rb") as image_file:
                            image_data = compress_and_encode(image_file)
                        content_list.append({
                            "type": "text",
                            "text": """
                                You are given:
                                - Before/after preprocessing comparison plots
                                - Reference image showing well-preprocessed neural signals

                                QUALITY EVALUATION CHECKLIST:
                                ✅ **GOOD PREPROCESSING INDICATORS**:
                                - Stable baseline (no drift or DC offset)
                                - Clear, sharp spike waveforms preserved
                                - Reduced background noise without oversmoothing
                                - Consistent amplitude scaling across time
                                - No filtering artifacts or ringing

                                ❌ **POOR PREPROCESSING INDICATORS**:
                                - Baseline still drifting or unstable
                                - Spikes blurred, distorted, or missing
                                - Excessive noise or artifacts remaining
                                - Signal appears overfiltered (too smooth)
                                - Channel-to-channel inconsistencies

                                YOUR EVALUATION PROCESS:
                                1. **COMPARE TO REFERENCE**: Use the provided reference image as quality standard
                                2. **ASSESS EACH CRITERION**: Check every item in the quality checklist
                                3. **IDENTIFY SPECIFIC ISSUES**: Point out exact problems you observe
                                4. **RATE OVERALL QUALITY**: Good enough for spike sorting, or needs improvement?

                                IF PREPROCESSING IS SATISFACTORY:
                                - Describe what improvements were achieved
                                - Confirm signal is ready for spike sorting
                                - **ASK USER**: "✅ Step 3 (Signal Assessment & Preprocessing) is complete. The neural signals have been filtered and cleaned with quality validation. Would you like me to proceed to Step 4 (Spike Sorting), or would you like to review the preprocessing results or adjust any parameters first?"
                                - **WAIT** for user response before proceeding

                                IF PREPROCESSING NEEDS IMPROVEMENT:
                                🔄 **REPROCESSING ATTEMPT LIMIT**: You may try reprocessing **MAXIMUM 2 TIMES**
                                
                                For attempt 1-2:
                                1. **RELOAD ORIGINAL**: `recording = si.load(recording_folder)`
                                2. **ADJUST STRATEGY**: Try different parameters or methods
                                3. **RE-EXECUTE**: Apply new preprocessing pipeline
                                4. **RE-VALIDATE**: Call plot_filter_comparison() again

                                🛑 **AFTER 2 ATTEMPTS**: If quality is still not ideal:
                                - **ACCEPT CURRENT RESULTS**: "Preprocessing has been optimized within reasonable limits"
                                - **INFORM USER**: "Preprocessing could be further improved, but proceeding with current quality to avoid overprocessing"
                                - **ASK USER**: "✅ Step 3 (Signal Assessment & Preprocessing) is complete with optimized preprocessing. Would you like me to proceed to Step 4 (Spike Sorting), or would you like to review the results first?"
                                - **WAIT** for user response before proceeding

                                💡 **FALLBACK OPTION**: If completely unable to improve:
                                - Use minimal preprocessing (bandpass + common reference only)
                                - Still ask for user confirmation before Step 4

                                **NEVER** proceed to Step 4 without explicit user permission (unless in autonomous end-to-end mode).
                            """
                        })
                        content_list.append({"type": "image_url",
                        "image_url": {"url": f"data:image/png;base64,{image_data}"}})
                else:
                    content_list.append({
                        "type": "text",
                        "text": """
                            **Analyze the visual output from the code above to determine the next step.**

                            **1. If the plots was successfully generated:**
                            - Describe in detail what the plot shows in the context of our current goal and step.
                            - Propose the next immediate action or code to execute in the current context.

                            **2. If no plot was generated or it shows an error:**
                            - Review the preceding code block that was intended to create the plot.
                            - Identify the likely cause of the failure (e.g., error in the code, unexpected data).
                            - Propose a corrected version of the code to fix the issue.
                            
                            PLEASE USE EXPLICITLY STATE YOUR RESPONSE TO THE USER.
                        """
                    })

            if len(content_list) > 1:
                image_message = HumanMessage(content=content_list, name="image_assistant")
                state["messages"].append(image_message)

        response = llm.invoke(state["messages"])

        if response.tool_calls:
            return Command(
                update={"messages": [response]},
                goto="tools",
            )
        else:
            st.session_state["render_last_message"] = True
            return Command(
                update={"messages": [response]},
                goto="__end__",
            )

    return _call_model


python_repl = PythonREPL()
@tool(response_format="content_and_artifact")
def python_repl_tool(query: str) -> Tuple[str, List[str]]:
    """A Python shell. Use this to execute python commands. Input should be a valid python command. 
    If you want to see the output of a value, you should print it out with `print(...)`. 
    If you run into error related to functions in spikeinterface, you can use the 'ask_spikeinterface_doc' tool to get more information"""
    
    plot_paths = []  # List to store file paths of generated plots
    result_parts = []  # List to store different parts of the output
    
    try:
        output = python_repl.run(query)
        if output and output.strip():
            result_parts.append(output.strip())
        
        figures = [plt.figure(i) for i in plt.get_fignums()]
        if figures:
            for fig in figures:
                # Generate filename
                plot_filename = f"plot_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}.png"
                # Create relative path
                rel_path = os.path.join(tmp_folder, plot_filename)
                # Convert to absolute path for saving
                abs_path = os.path.join(os.path.dirname(__file__), rel_path)
                
                fig.savefig(abs_path)
                plot_paths.append(rel_path)  # Store relative path
            
            plt.close("all")
            result_parts.append(f"Generated {len(plot_paths)} plot(s).")
        
        if not result_parts:  # If no output and no figures
            result_parts.append("Executed code successfully with no output. If you want to see the output of a value, you should print it out with `print(...)`.")

    except Exception as e:
        result_parts.append(f"Error executing code: {e}")
    
    # Join all parts of the result with newlines
    result_summary = "\n".join(result_parts)
    
    # Return both the summary and plot paths (if any)
    return result_summary, plot_paths


class ConversationSummary(BaseModel):
    """Structure for conversation title and summary."""
    title: str = Field(description="The title of the conversation")
    summary: str = Field(description="A concise summary of the conversation's main points")



def get_conversation_summary(messages: List[BaseMessage], selected_model) -> Tuple[str, str]:
    llm = get_model(selected_model)
    prompt_template = ChatPromptTemplate.from_messages([
        MessagesPlaceholder("msgs"),
        ("human", "Given the above messages between user and AI agent, return a title and concise summary of the conversation"),
    ])
    structured_llm = llm.with_structured_output(ConversationSummary)
    summarized_chain = prompt_template | structured_llm
    response = summarized_chain.invoke(messages)
    return response.title, response.summary
