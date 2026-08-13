import streamlit as st
import time
import os
from datetime import datetime

st.set_page_config(
    page_title="NEON CORE // AI",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

GROQ_API_KEY = st.secrets.get("GROQ_API_KEY", os.environ.get("GROQ_API_KEY", ""))
PINECONE_API_KEY = st.secrets.get("PINECONE_API_KEY", os.environ.get("PINECONE_API_KEY", ""))
TAVILY_API_KEY = st.secrets.get("TAVILY_API_KEY", os.environ.get("TAVILY_API_KEY", ""))

missing_keys = []
if not GROQ_API_KEY:
    missing_keys.append("GROQ_API_KEY")
if not PINECONE_API_KEY:
    missing_keys.append("PINECONE_API_KEY")
if not TAVILY_API_KEY:
    missing_keys.append("TAVILY_API_KEY")

if missing_keys:
    st.error("MISSING REQUIRED SECRETS: " + ", ".join(missing_keys))
    st.info("Add these keys to your Streamlit Cloud secrets.toml file, then reboot the app.")
    st.stop()

os.environ["TAVILY_API_KEY"] = TAVILY_API_KEY

from langchain_groq import ChatGroq
from langchain_community.tools.tavily_search import TavilySearchResults
from pinecone import Pinecone, ServerlessSpec

CHANNELS = ["SYSTEM_MAIN_01", "RESEARCH_LOGS", "PROJECT_ALPHA"]
INDEX_NAME = "infinite-context"
EMBED_MODEL = "multilingual-e5-large"
EMBED_DIMENSION = 1024

NEON_CSS = """
<style>
html, body, [class*="css"] {
    background-color: #000000 !important;
    color: #39ff14 !important;
    font-family: 'Courier New', monospace !important;
}
.stApp {
    background-color: #000000;
}
h1, h2, h3 {
    color: #39ff14 !important;
    text-shadow: 0 0 8px #39ff14, 0 0 16px #39ff14;
}
.stTextInput input, .stTextArea textarea {
    background-color: #000000 !important;
    color: #39ff14 !important;
    border: 1px solid #ff6a00 !important;
    box-shadow: 0 0 6px #ff6a00;
}
.stButton button {
    background-color: #000000 !important;
    color: #ff0000 !important;
    border: 1px solid #ff0000 !important;
    box-shadow: 0 0 8px #ff0000;
    font-weight: bold;
}
.stButton button:hover {
    color: #39ff14 !important;
    border: 1px solid #39ff14 !important;
    box-shadow: 0 0 10px #39ff14;
}
section[data-testid="stSidebar"] {
    background-color: #000000 !important;
    border-right: 1px solid #ff6a00;
}
.user-bubble {
    border: 1px solid #ff6a00;
    box-shadow: 0 0 6px #ff6a00;
    color: #ff6a00;
    padding: 10px;
    border-radius: 4px;
    margin-bottom: 10px;
    background-color: #000000;
}
.ai-bubble {
    border: 1px solid #39ff14;
    box-shadow: 0 0 6px #39ff14;
    color: #39ff14;
    padding: 10px;
    border-radius: 4px;
    margin-bottom: 10px;
    background-color: #000000;
}
.stSelectbox div[data-baseweb="select"] {
    background-color: #000000 !important;
    border: 1px solid #ff0000 !important;
    box-shadow: 0 0 6px #ff0000;
}
hr {
    border-color: #ff0000 !important;
}
</style>
"""

st.markdown(NEON_CSS, unsafe_allow_html=True)


@st.cache_resource
def get_pinecone_client():
    pc = Pinecone(api_key=PINECONE_API_KEY)
    existing_indexes = [idx["name"] for idx in pc.list_indexes()]
    if INDEX_NAME not in existing_indexes:
        pc.create_index(
            name=INDEX_NAME,
            dimension=EMBED_DIMENSION,
            metric="cosine",
            spec=ServerlessSpec(cloud="aws", region="us-east-1")
        )
    return pc


@st.cache_resource
def get_llm():
    llm = ChatGroq(
        groq_api_key=GROQ_API_KEY,
        model_name="openai/gpt-oss-120b",
        temperature=0.6
    )
    return llm


@st.cache_resource
def get_search_tool():
    tool = TavilySearchResults(max_results=4)
    return tool


pc_client = get_pinecone_client()
pc_index = pc_client.Index(INDEX_NAME)
llm = get_llm()
search_tool = get_search_tool()


def embed_text(text_value, input_type):
    result = pc_client.inference.embed(
        model=EMBED_MODEL,
        inputs=[text_value],
        parameters={"input_type": input_type, "truncate": "END"}
    )
    vector_values = result[0]["values"]
    return vector_values


def store_chat_message(text_value, role_value, channel_value):
    vector_id = role_value + "_" + channel_value + "_" + str(time.time())
    vector_values = embed_text(text_value, "passage")
    metadata = {
        "text": text_value,
        "role": role_value,
        "type": "chat",
        "channel": channel_value,
        "timestamp": time.time()
    }
    pc_index.upsert(vectors=[{"id": vector_id, "values": vector_values, "metadata": metadata}])


def store_knowledge_text(text_value):
    vector_id = "knowledge_" + str(time.time())
    vector_values = embed_text(text_value, "passage")
    metadata = {
        "text": text_value,
        "type": "knowledge"
    }
    pc_index.upsert(vectors=[{"id": vector_id, "values": vector_values, "metadata": metadata}])


def fetch_channel_history(channel_value):
    query_vector = embed_text("conversation history signature for " + channel_value, "query")
    filter_condition = {
        "type": {"$eq": "chat"},
        "channel": {"$eq": channel_value}
    }
    query_response = pc_index.query(
        vector=query_vector,
        top_k=50,
        filter=filter_condition,
        include_metadata=True
    )
    matches = query_response.get("matches", [])
    history_items = []
    for match_item in matches:
        meta = match_item.get("metadata", {})
        history_items.append(meta)
    history_items.sort(key=lambda item: item.get("timestamp", 0))
    return history_items


def fetch_knowledge_chunks(prompt_value):
    query_vector = embed_text(prompt_value, "query")
    filter_condition = {
        "type": {"$eq": "knowledge"}
    }
    query_response = pc_index.query(
        vector=query_vector,
        top_k=5,
        filter=filter_condition,
        include_metadata=True
    )
    matches = query_response.get("matches", [])
    chunk_texts = []
    for match_item in matches:
        meta = match_item.get("metadata", {})
        chunk_text = meta.get("text", "")
        if chunk_text:
            chunk_texts.append(chunk_text)
    return chunk_texts


def run_web_search(prompt_value):
    try:
        search_results = search_tool.invoke({"query": prompt_value})
    except Exception:
        return "WEB SEARCH UNAVAILABLE"
    result_lines = []
    if isinstance(search_results, list):
        for item in search_results:
            if isinstance(item, dict):
                snippet = item.get("content", "")
                source_url = item.get("url", "")
                result_lines.append(snippet + " (SOURCE: " + source_url + ")")
    summary_text = "\n".join(result_lines)
    if not summary_text:
        summary_text = "NO RELEVANT WEB RESULTS FOUND"
    return summary_text


def build_history_string(history_items):
    line_list = []
    for item in history_items:
        role_label = item.get("role", "unknown")
        text_value = item.get("text", "")
        line_list.append(role_label.upper() + ": " + text_value)
    history_string = "\n".join(line_list)
    return history_string


def generate_ai_response(prompt_value, history_string, knowledge_chunks, web_summary):
    knowledge_string = "\n".join(knowledge_chunks)

    system_instructions = (
        "You are NEON CORE, an elite cyberpunk AI terminal assistant. "
        "Respond with precision, confidence, and a slight cyberpunk terminal tone. "
        "Use the provided conversation history, stored knowledge, and live web data "
        "to answer accurately. Do not fabricate facts."
    )

    combined_context = (
        "CONVERSATION HISTORY:\n" + history_string +
        "\n\nSTORED KNOWLEDGE:\n" + knowledge_string +
        "\n\nLIVE WEB SEARCH SUMMARY:\n" + web_summary +
        "\n\nCURRENT USER PROMPT:\n" + prompt_value
    )

    message_payload = [
        ("system", system_instructions),
        ("human", combined_context)
    ]

    response_object = llm.invoke(message_payload)
    response_text = response_object.content
    return response_text


if "active_channel" not in st.session_state:
    st.session_state.active_channel = CHANNELS[0]

if "loaded_channels" not in st.session_state:
    st.session_state.loaded_channels = {}

if "pending_prompt" not in st.session_state:
    st.session_state.pending_prompt = ""


def handle_submit():
    submitted_text = st.session_state.chat_input_box
    if submitted_text.strip():
        st.session_state.pending_prompt = submitted_text
    st.session_state.chat_input_box = ""


with st.sidebar:
    st.markdown("### ⚡ CHANNEL SELECT ⚡")
    selected_channel = st.selectbox(
        "ACTIVE COMM CHANNEL",
        CHANNELS,
        index=CHANNELS.index(st.session_state.active_channel)
    )
    if selected_channel != st.session_state.active_channel:
        st.session_state.active_channel = selected_channel
        if selected_channel in st.session_state.loaded_channels:
            del st.session_state.loaded_channels[selected_channel]

    st.markdown("---")
    st.markdown("### 🧠 INFINITE MEMORY UPLOAD")
    knowledge_input = st.text_area("PASTE RAW TEXT INTO KNOWLEDGE CORE", height=200, key="knowledge_input_box")
    if st.button("INJECT INTO PINECONE"):
        if knowledge_input.strip():
            store_knowledge_text(knowledge_input.strip())
            st.success("KNOWLEDGE UPLOADED SUCCESSFULLY")
        else:
            st.warning("NO TEXT PROVIDED")

    st.markdown("---")
    st.markdown("### 🛰️ SYSTEM STATUS")
    st.markdown("GROQ LINK: **ONLINE**")
    st.markdown("PINECONE LINK: **ONLINE**")
    st.markdown("TAVILY LINK: **ONLINE**")

st.markdown("# ⚡ NEON CORE // AI ⚡")
st.markdown("### TERMINAL CHANNEL: `" + st.session_state.active_channel + "`")
st.markdown("---")

current_channel = st.session_state.active_channel

if current_channel not in st.session_state.loaded_channels:
    with st.spinner("SYNCING CHANNEL HISTORY FROM PINECONE..."):
        loaded_history = fetch_channel_history(current_channel)
    st.session_state.loaded_channels[current_channel] = loaded_history

channel_history = st.session_state.loaded_channels[current_channel]

chat_container = st.container()
with chat_container:
    for history_item in channel_history:
        role_value = history_item.get("role", "user")
        text_value = history_item.get("text", "")
        if role_value == "user":
            st.markdown("<div class='user-bubble'><b>OPERATOR:</b> " + text_value + "</div>", unsafe_allow_html=True)
        else:
            st.markdown("<div class='ai-bubble'><b>NEON CORE:</b> " + text_value + "</div>", unsafe_allow_html=True)

st.markdown("---")

with st.form(key="prompt_form", clear_on_submit=True):
    user_prompt = st.text_input("TRANSMIT MESSAGE >>", key="chat_input_box")
    submit_button = st.form_submit_button("TRANSMIT", on_click=handle_submit)

if st.session_state.pending_prompt:
    active_prompt = st.session_state.pending_prompt
    st.session_state.pending_prompt = ""

    store_chat_message(active_prompt, "user", current_channel)
    st.session_state.loaded_channels[current_channel].append({
        "text": active_prompt,
        "role": "user",
        "type": "chat",
        "channel": current_channel,
        "timestamp": time.time()
    })

    with st.spinner("QUERYING PINECONE KNOWLEDGE CORE..."):
        knowledge_chunks = fetch_knowledge_chunks(active_prompt)

    with st.spinner("SCANNING LIVE WEB CHANNELS..."):
        web_summary = run_web_search(active_prompt)

    history_string = build_history_string(channel_history)

    with st.spinner("GENERATING RESPONSE..."):
        ai_response_text = generate_ai_response(active_prompt, history_string, knowledge_chunks, web_summary)

    store_chat_message(ai_response_text, "ai", current_channel)
    st.session_state.loaded_channels[current_channel].append({
        "text": ai_response_text,
        "role": "ai",
        "type": "chat",
        "channel": current_channel,
        "timestamp": time.time()
    })

    st.rerun()
