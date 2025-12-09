# spike_agent_app.py
import os
import json
import inspect
import subprocess
import shutil
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

import streamlit as st

from langchain_core.messages import AIMessage, HumanMessage, ToolMessage, SystemMessage
from langchain.tools import tool
from spikeagent.app.graph import Graph_generator, get_conversation_summary, python_repl_tool
from spikeagent.app.st_utils.st_display import render_conversation_history
from spikeagent.app.st_utils.speech_to_text import input_from_mic, convert_text_to_speech
from spikeagent.app.st_utils.comp_img import compress_and_encode
from spikeagent.app.st_utils.read_config import read_config
from spikeagent.app import tool as app_tools
from spikeagent.curation import (
    get_guidance_on_rigid_curation,
    get_guidance_on_vlm_curation,
    get_guidance_on_vlm_merge_analysis,
    get_guidance_on_save_final_results,
)

# Combine app tools and curation tools
mytools = app_tools
# Add curation functions to mytools namespace
for name in ['get_guidance_on_rigid_curation', 'get_guidance_on_vlm_curation', 
             'get_guidance_on_vlm_merge_analysis', 'get_guidance_on_save_final_results']:
    setattr(mytools, name, globals()[name])

# Load environment
load_dotenv()

# Helper functions for dynamic mounting
def check_mount_capabilities():
    """Check if container has mount capabilities"""
    try:
        # Check if we can read /proc/self/status for capabilities
        with open('/proc/self/status', 'r') as f:
            status = f.read()
            if 'CapEff:' in status:
                # Check if we have SYS_ADMIN capability (needed for mount)
                try:
                    result = subprocess.run(['capsh', '--print'], 
                                          capture_output=True, text=True, timeout=2)
                    if 'SYS_ADMIN' in result.stdout or '=ep' in result.stdout:
                        return True
                except (FileNotFoundError, subprocess.TimeoutExpired):
                    pass
    except:
        pass
    
    # Fallback: try to check if we're in privileged mode
    try:
        # Check if /proc/sys/kernel/core_pattern is writable (indicator of privileges)
        test_path = '/proc/sys/kernel/core_pattern'
        if os.access(test_path, os.W_OK):
            return True
    except:
        pass
    
    return False

def try_mount_path(host_path, container_path=None):
    """Try to mount a path using bind mount"""
    if container_path is None:
        # Use same path in container
        container_path = host_path
    
    # Create mount point if it doesn't exist
    try:
        os.makedirs(container_path, exist_ok=True)
    except:
        pass
    
    try:
        # Try bind mount
        result = subprocess.run(
            ['mount', '--bind', host_path, container_path],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            return True, f"Successfully mounted {host_path}"
        else:
            return False, f"Mount failed: {result.stderr}"
    except subprocess.TimeoutExpired:
        return False, "Mount operation timed out"
    except FileNotFoundError:
        return False, "mount command not available"
    except Exception as e:
        return False, f"Mount error: {str(e)}"

def generate_restart_command(paths):
    """Generate the restart command with volume mounts"""
    if isinstance(paths, str):
        paths = [paths]
    paths_str = " ".join([f'"{p}"' if " " in p else p for p in paths if p])
    return f'./run-spikeagent.sh {paths_str}'

# Streamlit setup
st.set_page_config(layout='wide')
_app_dir = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(_app_dir, "style.css")) as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

st.markdown('<h1 class="main-title"> 🤖 Spike Agent</h1>', unsafe_allow_html=True)

# Session State Initialization
def init_session():
    if "final_state" not in st.session_state:
        _app_dir = os.path.dirname(os.path.abspath(__file__))
        with open(os.path.join(_app_dir, "prompt.txt"), 'r') as f:
            content = f.read()
            st.session_state.final_state = {"messages": [SystemMessage(content=content)]}
    st.session_state.setdefault("audio_transcription", None)
    st.session_state.setdefault("last_summary_point", 0)
    st.session_state.setdefault("last_summary_title", "Default Title")
    st.session_state.setdefault("last_summary_summary", "This is the default summary for short conversations.")
    st.session_state.setdefault("not_render_idx", [])
    st.session_state.setdefault("clear_params", False)
    # Initialize API keys from environment variables
    if os.getenv("OPENAI_API_KEY") and "OPENAI_API_KEY" not in st.session_state:
        st.session_state["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
    if os.getenv("ANTHROPIC_API_KEY") and "ANTHROPIC_API_KEY" not in st.session_state:
        st.session_state["ANTHROPIC_API_KEY"] = os.getenv("ANTHROPIC_API_KEY")
    if os.getenv("GOOGLE_API_KEY") and "GOOGLE_API_KEY" not in st.session_state:
        st.session_state["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY")
    # Set environment variables from session state
    if "OPENAI_API_KEY" in st.session_state:
        os.environ["OPENAI_API_KEY"] = st.session_state["OPENAI_API_KEY"]
    if "ANTHROPIC_API_KEY" in st.session_state:
        os.environ["ANTHROPIC_API_KEY"] = st.session_state["ANTHROPIC_API_KEY"]
    if "GOOGLE_API_KEY" in st.session_state:
        os.environ["GOOGLE_API_KEY"] = st.session_state["GOOGLE_API_KEY"]

init_session()

# Sidebar Provider & Model Selection
st.sidebar.title("🎯 Navigation")
PROVIDER_CONFIGS = {
    "OpenAI":     {"icon": "🟢", "color": "#11AA84"},
    "Anthropic":  {"icon": "🟣", "color": "#6B48FF"},
    "Gemini":     {"icon": "🔵", "color": "#1E88E5"},
}
provider_options = [f"{v['icon']} {k}" for k, v in PROVIDER_CONFIGS.items()]
selected = st.sidebar.radio("Select LLM Provider Family", provider_options, key='uniq1')
page = selected.split(" ")[1]

# Initialize API keys from environment or session state (no UI inputs)
if "OPENAI_API_KEY" in st.session_state:
    os.environ["OPENAI_API_KEY"] = st.session_state["OPENAI_API_KEY"]
elif os.getenv("OPENAI_API_KEY"):
    st.session_state["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

if "ANTHROPIC_API_KEY" in st.session_state:
    os.environ["ANTHROPIC_API_KEY"] = st.session_state["ANTHROPIC_API_KEY"]
elif os.getenv("ANTHROPIC_API_KEY"):
    st.session_state["ANTHROPIC_API_KEY"] = os.getenv("ANTHROPIC_API_KEY")

if "GOOGLE_API_KEY" in st.session_state:
    os.environ["GOOGLE_API_KEY"] = st.session_state["GOOGLE_API_KEY"]
elif os.getenv("GOOGLE_API_KEY"):
    st.session_state["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY")

# Track provider changes
if "current_provider" not in st.session_state:
    st.session_state.current_provider = page
elif st.session_state.current_provider != page:
    # Provider changed, reset model selection
    st.session_state.current_provider = page
    if "selected_model" in st.session_state:
        del st.session_state.selected_model
    if "graph_runnable" in st.session_state:
        del st.session_state.graph_runnable

os.makedirs('history', exist_ok=True)
MODEL_CONFIG = {
    "OpenAI":     ("./history/conversation_histories_gpt", ["gpt-4o", "gpt-4o-mini", "gpt-4.1", "o1", "gpt-4-turbo", "gpt-3.5-turbo"]),
    "Gemini":     ("./history/conversation_histories_gemini", ["gemini-2.5-pro","gemini-2.0-flash-exp", "gemini-1.5-flash", "gemini-1.5-flash-8b", "gemini-1.5-pro"]),
    "Anthropic":  ("./history/conversation_histories_anthropic", ["claude_4_sonnet", "claude_4_opus", "claude_3_5_sonnet", "claude_3_7_sonnet", "claude_3_opus", "claude_3_haiku", "claude_3_sonnet"]),
}
HISTORY_DIR, available_models = MODEL_CONFIG[page]
os.makedirs(HISTORY_DIR, exist_ok=True)

tools = [
    tool(getattr(mytools, name))
    for name in dir(mytools)
    if inspect.isfunction(getattr(mytools, name))
]

if page == "Gemini":
    tools += [python_repl_tool] #python_repl_tool_for_gemini
else:
    tools += [python_repl_tool]

# Model Selection State - ensure graph_runnable is always initialized
if "selected_model" not in st.session_state:
    st.session_state.selected_model = available_models[0]

# Get current selected model from selectbox
selected_model = st.sidebar.selectbox(f"🔧 Select {page} Model:", available_models, 
                                     index=available_models.index(st.session_state.selected_model) if st.session_state.selected_model in available_models else 0)

# Initialize or reinitialize graph_runnable if needed
if "graph_runnable" not in st.session_state or selected_model != st.session_state.selected_model:
    try:
        st.session_state.graph_runnable = Graph_generator(selected_model, tools)
        st.session_state.selected_model = selected_model
    except Exception as e:
        st.error(f"Error initializing model: {e}")
        st.stop()

# Clear & Reset Conversation
def clear_conversation():
    for key in ["final_state", "audio_transcription", "not_render_idx", "clear_params", "last_summary_title", "last_summary_summary", "last_summary_point"]:
        if key in st.session_state:
            del st.session_state[key]
    # Don't delete graph_runnable or selected_model - they're needed
    render_conversation_history([])

# Model change is now handled above in the initialization section

# New Chat
if st.sidebar.button("🔄 Start New Chat"):
    clear_conversation()
    st.rerun()

# API Key Handling - Check if key is set (from top section or environment)
api_keys = {"OpenAI": "OPENAI_API_KEY", "Gemini": "GOOGLE_API_KEY", "Anthropic": "ANTHROPIC_API_KEY"}
api_key = os.getenv(api_keys[page])
if not api_key:
    # Fallback to sidebar if not set in top section
    st.sidebar.markdown(f"""<div class="api-key-setup"><h3>🔑 {page} API Key Setup</h3></div>""", unsafe_allow_html=True)
    api_key = st.sidebar.text_input(f"{page} API Key", type="password", label_visibility="collapsed")
    if api_key:
        os.environ[api_keys[page]] = api_key
    else:
        st.warning(f"⚠️ Please enter your {page} API Key in the API Keys Configuration section at the top or in the sidebar.")
        st.stop()

# Helper Functions
def save_history(title, summary):
    data = {
        "title": title,
        "summary": summary,
        "timestamp": datetime.now().isoformat(),
        "messages": [msg.dict() for i,msg in enumerate(st.session_state.final_state["messages"]) 
                     if not isinstance(msg, SystemMessage) 
                     and i not in st.session_state.not_render_idx]
    }
    path = os.path.join(HISTORY_DIR, f"{title.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
    with open(path, "w") as f:
        json.dump(data, f)
    st.rerun()

def load_all_histories():
    files = [f for f in os.listdir(HISTORY_DIR) if f.endswith(".json")]
    def load_file(f):
        with open(os.path.join(HISTORY_DIR, f), "r") as file:
            j = json.load(file)
            return {"title": j["title"], "summary": j["summary"], "timestamp": j["timestamp"], "filename": f}
    return sorted([load_file(f) for f in files], key=lambda x: x["timestamp"], reverse=True)

def load_history(filename):
    with open(os.path.join(HISTORY_DIR, filename), "r") as f:
        data = json.load(f)
        load_message = []
        for m in data["messages"]:
            if m['type'] == "ai":
                load_message.append(AIMessage(**m))
            elif m['type'] == "human":
                load_message.append(HumanMessage(**m))
            elif m['type'] == "tool":
                load_message.append(ToolMessage(**m))
            else:
                continue     
        st.session_state.final_state["messages"] = load_message

        st.sidebar.success(f"Conversation '{data['title']}' loaded successfully")

def delete_history(filename):
    os.remove(os.path.join(HISTORY_DIR, filename))
    st.sidebar.success("Conversation history deleted.")
    st.rerun()


with st.sidebar.expander("#### Pipeline Settings", expanded=False, icon="⚙️"):
    autonomous_run = st.button("🚀 Run End to End", use_container_width=True)

    # Raw Data Path
    st.markdown("**📂 Raw Data Path**")
    raw_path_value = st.session_state.get("raw_path_input", "")
    raw_path = st.text_input(
        "Raw data path", 
        value=raw_path_value,
        key="raw_path_input",
        label_visibility="collapsed",
        placeholder="Enter path to your data..."
    )
    
    # Validate raw_path
    if raw_path:
        if os.path.exists(raw_path):
            st.success(f"✅ Path accessible: `{raw_path}`")
        else:
            st.warning(f"⚠️ Path not found: `{raw_path}`")
            st.info("""
            **📌 Note:** Docker containers cannot mount new volumes at runtime. 
            You need to restart the container with this path mounted.
            """)
            
            # Show restart command
            with st.expander("🔧 How to mount this path", expanded=True):
                st.markdown("**Option 1: Restart with this path**")
                cmd = generate_restart_command([raw_path])
                st.code(cmd, language="bash")
                st.caption("This will stop the current container and restart it with the new mount.")
                
                st.markdown("**Option 2: Add to existing mounts (preserves current mounts)**")
                # Escape the path for shell if it contains spaces
                escaped_path = raw_path.replace(" ", "\\ ") if " " in raw_path else raw_path
                st.code(f"./run-spikeagent.sh --add {escaped_path}", language="bash")
                st.caption("Use --add to add this path to existing mounts without losing current ones.")
                
                # Try to detect existing mounts and suggest adding to them
                try:
                    # Check if we can detect container name
                    container_id = os.environ.get('HOSTNAME', '')
                    if container_id:
                        st.markdown("**Current container:**")
                        st.code(f"docker ps --filter name=spikeagent", language="bash")
                except:
                    pass
    
    # Save Path with validation
    st.markdown("**📁 Save Path**")
    save_path = st.text_input("Save_path", value="", key="save_path_input")
    
    if save_path:
        if os.path.exists(save_path):
            st.success(f"✅ Path accessible: `{save_path}`")
        else:
            # Try to create it
            try:
                os.makedirs(save_path, exist_ok=True)
                st.info(f"📁 Created save path: `{save_path}`")
            except Exception as e:
                st.warning(f"⚠️ Cannot create save path: {e}")
                parent_dir = os.path.dirname(save_path) if save_path else "/tmp"
                st.info("""
                **📌 Note:** Docker containers cannot mount new volumes at runtime. 
                You need to restart the container with this path mounted.
                """)
                
                with st.expander("🔧 How to mount this path", expanded=True):
                    st.markdown("**Option 1: Restart with this path**")
                    cmd = generate_restart_command([parent_dir])
                    st.code(cmd, language="bash")
                    
                    st.markdown("**Option 2: Add to existing mounts (preserves current mounts)**")
                    escaped_path = parent_dir.replace(" ", "\\ ") if " " in parent_dir else parent_dir
                    st.code(f"./run-spikeagent.sh --add {escaped_path}", language="bash")
    
    is_npix = st.checkbox("Is it neuropixel data?", value=False, key="ch1")
    commands = st.text_area("⚙️ Additional inputs", value="", height=150)

    at_prompt = f"""You will now execute the entire pipeline autonomously.
        You are not allowed to request any additional inputs during execution — simply clarify your actions and proceed.
        Run the pipeline from start to finish without interruption. Determine the most appropriate parameters based on the data yourself.

        The following parameters are provided:
        ------------------------------
        raw data path: {raw_path}
        save_path: {save_path}
        is neuropixel: {is_npix}
        additional commands: {commands}
        ------------------------------
        Use these inputs as given. For all other parameters not listed above, you must make your own decisions.
        Execute the entire pipeline end-to-end."""
    



# Sidebar Tabs
st.sidebar.title("⚙️ Settings")
tab1, tab2, tab3 = st.sidebar.tabs(["💬 Conversation", "🎤 Voice", "🖼️ Image"])

# Conversation Tab
with tab1:
    st.subheader("History")
    for h in load_all_histories():
        with st.expander(f"{h['title']} ({h['timestamp'][:10]})"):
            st.write(h["summary"])
            if st.button("Load", key=f"load_{h['filename']}"):
                load_history(h["filename"])
            if st.button("Delete", key=f"delete_{h['filename']}"):
                delete_history(h["filename"])

    msg_count = len(st.session_state.final_state["messages"])
    if msg_count > 30 and (msg_count - 5) % 50 == 0 and msg_count != st.session_state.last_summary_point:
        title, summary = get_conversation_summary(st.session_state.final_state["messages"], selected_model)
        st.session_state.last_summary_title = title
        st.session_state.last_summary_summary = summary
        st.session_state.last_summary_point = msg_count

    title = st.text_input("Conversation Title", value=st.session_state.last_summary_title)
    summary = st.text_area("Conversation Summary", value=st.session_state.last_summary_summary)
    if st.button("Save Conversation"):
        save_history(title, summary)

# Voice Tab
with tab2:
    st.subheader("Audio Options")
    use_audio_input = st.checkbox("Enable Voice Input", value=False)
    if use_audio_input:
        with st.form("audio_input_form", clear_on_submit=True):
            st.markdown("<div class='audio-instructions'> ... </div>", unsafe_allow_html=True)
            if st.form_submit_button("Submit Audio"):
                st.session_state.audio_transcription = input_from_mic()

    use_voice_response = st.checkbox("Enable Voice Response", value=False)
    if use_voice_response:
        st.write("Long responses will be summarized.")

# Image Tab
with tab3:
    st.subheader("Image")
    with st.form("image_upload_form", clear_on_submit=True):
        uploaded = st.file_uploader("Upload one or more images", type=["jpg", "jpeg", "png"], accept_multiple_files=True)
        if st.form_submit_button("Submit Images"):
            st.session_state.uploaded_images_data = [compress_and_encode(img) for img in uploaded] if uploaded else []

# Generate Response Logic
def generate_response(human_input, render=True):
    content = [{"type": "text", "text": human_input}]
    if imgs := st.session_state.get("uploaded_images_data"):
        content.extend([{"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img}"}} for img in imgs])
        st.session_state.uploaded_images_data = []

    msg = HumanMessage(content=content)
    st.session_state.final_state["messages"].append(msg)

    if render:
        render_conversation_history([msg])
    else:
        st.session_state.not_render_idx.append(len(st.session_state.final_state["messages"]) - 1)

    with st.spinner("Agent is thinking..."):
        prev_len = len(st.session_state.final_state["messages"])
        updated = st.session_state.graph_runnable.invoke_our_graph(st.session_state.final_state["messages"])
        st.session_state.final_state = updated
        new_messages = updated["messages"][prev_len:]

    if st.session_state.get("render_last_message", True):
        render_conversation_history([new_messages[-1]])

    if st.session_state.get("audio_transcription"):
        st.session_state.audio_transcription = None

    if st.session_state.get("use_voice_response"):
        audio = convert_text_to_speech(new_messages[-1].content)
        if audio:
            st.audio(audio)

# Main Prompt Interaction
st.markdown(f"""
    <div class="chat-title">
        <span class="robot-icon">🤖</span>
        <span>Chat with <span class="provider-name">{page}</span> Agent</span>
    </div>
""", unsafe_allow_html=True)

render_conversation_history([
    m for i, m in enumerate(st.session_state.final_state["messages"])
    if i not in st.session_state.not_render_idx
])


prompt = st.session_state.get("audio_transcription") or st.chat_input()
        
if autonomous_run:
    generate_response(at_prompt, render=False)
if prompt:
    generate_response(prompt)
