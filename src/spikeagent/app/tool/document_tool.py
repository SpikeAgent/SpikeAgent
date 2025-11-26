from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os

load_dotenv(override=True)
from spikeagent.app.tool.utils.custom_class_gemini import ChatGoogleGenerativeAI_H
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_anthropic import ChatAnthropic
from spikeagent.app.tool.utils.custom_class import ChatAnthropic_H
# Use a relative path to locate the documentation file
import pathlib
doc_path = pathlib.Path(__file__).parent.parent.parent / "app" / "spikeinterface_api_docs" / "merged_api.txt"

with open(doc_path, "r") as f:
    spikeinterface_api_doc = f.read()

def ask_spikeinterface_doc(question):
    """
    Query the LLM about the spikeinterface package using the provided API documentation.
    When user ask about the spikeinterface package, you should use this tool to answer the question.
    Or when SpikeAgent encounter some error that don't know how to solve, you should use this tool to get code to solve the error

    Parameters
    ----------
    question : str
        The user's question about the spikeinterface package.

    Returns
    -------
    str
        The LLM's answer, followed by a note for the agent.
    """
    prompt = (
        "You are an expert on the spikeinterface Python package.\n"
        "Below is the full API documentation for spikeinterface (merged_api.txt):\n\n"
        "--- BEGIN SPIKEINTERFACE API DOC ---\n"
        f"{spikeinterface_api_doc}\n"
        "--- END SPIKEINTERFACE API DOC ---\n\n"
        "Answer the following question using only the information in the documentation above.\n"
        "If the answer is not present, say \"The answer is not found in the provided documentation.\"\n\n"
        "DON'T WRAP in python brackets, as this will cause conflict with api\"\n\n"
        "DON'T WRAP in python brackets, as this will cause conflict with api\"\n\n"
        "when you return the result you should also return key parameters for the each function for user to understand how to use it"
        "you should also tell the user which module to import"
        "The answer should be detailed and include all the necessary information"
        f"Question: {question}\n"
    )
    
    # Try to use available API keys in priority order: OpenAI > Anthropic > Google
    if os.getenv("OPENAI_API_KEY"):
        openai_base_url = os.getenv("OPENAI_API_BASE")
        kwargs = {"model": "gpt-4.1", "temperature": 0}
        if openai_base_url:
            kwargs["base_url"] = openai_base_url
        llm = ChatOpenAI(**kwargs)
    elif os.getenv("HARVARD_API_KEY"):
        llm = ChatAnthropic_H(model="claude-3-5-sonnet-20240620-v1", temperature=0)
    elif os.getenv("ANTHROPIC_API_KEY"):
        llm = ChatAnthropic(model="claude-3-5-sonnet-20240620", temperature=0)
    elif os.getenv("HARVARD_API_KEY_GOOGLE") and os.getenv("GOOGLE_BASE_URL_HARVARD"):
        llm = ChatGoogleGenerativeAI_H(
            model="gemini-2.5-pro",
            temperature=0,
            client_options={"api_endpoint": os.getenv("GOOGLE_BASE_URL_HARVARD")},
            google_api_key=os.getenv("HARVARD_API_KEY_GOOGLE"),
            thinking_budget=200
        )
    elif os.getenv("GOOGLE_API_KEY"):
        llm = ChatGoogleGenerativeAI(model="gemini-1.5-pro", temperature=0)
    else:
        raise ValueError("No API key found. Please set OPENAI_API_KEY, ANTHROPIC_API_KEY, or GOOGLE_API_KEY in your .env file.")
    
    response = llm.invoke(prompt)

    note_for_agent = """

NOTE TO SpikeAgent:
The information above was retrieved from the documentation. you should adapt the code based on the current context 
If you need more information, you can use the `python_repl` tool to import the module and then use `help(module_name)` function to understand specific functions to get more in detail
"""
    return f"{response.content}{note_for_agent}"
