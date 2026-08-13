import os
import time
import streamlit as st
from langchain_groq import ChatGroq
from langchain_community.tools.tavily_search import TavilySearchResults
from pinecone import Pinecone

# 1. Page Canvas Initial Configurations
st.set_page_config(
    page_title="NEON CORE // AI", 
    page_icon="⚡", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

# 2. Cyberpunk Terminal Interface Stylesheet
st.markdown("""
    <style>
        .stApp { 
            background-color: #000000 !important; 
            color: #00FF66 !important; 
            font-family: 'Courier New', monospace;
        }
        section[data-testid="stSidebar"] { 
            background-color: #050505 !important; 
            border-right: 2px solid #FF5500 !important; 
        }
        h1, h2, h3, .sidebar-header { 
            color: #FF1100 !important; 
            text-transform: uppercase; 
            letter-spacing: 2px;
            font-weight: 900;
            text-shadow: 0px 0px 8px #FF1100;
        }
        .chat-container {
            margin: 15px 0px;
            padding: 15px;
            border-radius: 4px;
            width: 100%;
            clear: both;
        }
        .user-block {
            background-color: #0a0400;
            border: 1px solid #FF5500;
            border-left: 5px solid #FF5500;
            color: #FFBB00;
            box-shadow: 0px 0px 5px #FF5500;
        }
        .ai-block {
            background-color: #000a03;
            border: 1px solid #00FF66;
            border-left: 5px solid #00FF66;
            color: #33FF77;
            box-shadow: 0px 0px 5px #00FF66;
        }
        .stTextInput>div>div>input, .stTextArea>div>div>textarea, select {
            background-color: #080808 !important;
            color: #00FF66 !important;
            border: 1px solid #FF5500 !important;
            border-radius: 0px !important;
        }
        .stButton>button { 
            border-radius: 0px !important; 
            background-color: #FF5500 !important; 
            color: #000000 !important; 
            font-weight: bold !important;
            border: 1px solid #FF1100 !important;
            width: 100%;
        }
        .stButton>button:hover { 
            background-color: #00FF66 !important; 
            color: #000000 !important;
            box-shadow: 0px 0px 12px #00FF66;
        }
    </style>
""", unsafe_allow_html=True)

# 3. Environment Integrity Check
required_keys = ["GROQ_API_KEY", "PINECONE_API_KEY", "TAVILY_API_KEY"]
if not all(os.getenv(k) for k in required_keys):
    st.error("🚨 CONFIG FAULT: System variables undetected.")
    st.stop()

# 4. Global Hardware Client Hookups
@st.cache_resource
def load_llm():
    return ChatGroq(model="llama-3.3-70b-specdec", temperature=0.3, groq_api_key=os.getenv("GROQ_API_KEY"))

@st.cache_resource
def load_vector_db():
    pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
    return pc, pc.Index("infinite-context")

@st.cache_resource
def load_search():
    return TavilySearchResults(tavily_api_key=os.getenv("TAVILY_API_KEY"), max_results=3)

try:
    llm = load_llm()
    pc_client, index = load_vector_db()
    search_tool = load_search()
except Exception as e:
    st.error(f"❌ DATABASE/INFERENCE BOOT INTERCEPT EXCEPTION: {str(e)}")
    st.stop()

# 5. Core Control Sidebar Infrastructure Buildout
if "current_chat" not in st.session_state:
    st.session_state.current_chat = "SYSTEM_MAIN_01"

with st.sidebar:
    st.markdown('<div class="sidebar-header">⚡ NEON CORE // ENGINE</div>', unsafe_allow_html=True)
    
    # DYNAMIC STREAM MANAGEMENT ZONE
    st.markdown("<h3 style='color:#FF5500;'>[X] MATRIX_CHANNELS</h3>", unsafe_allow_html=True)
    new_chat_name = st.text_input("INITIALIZE PERMANENT STREAM:", placeholder="SECURE_LOG_X...")
    if st.button("⚡ EXECUTE STREAM FORWARDING") and new_chat_name:
        clean_name = new_chat_name.upper().replace(" ", "_")
        st.session_state.current_chat = clean_name
        st.rerun()

    # Pre-populate custom list options
    chat_list = ["SYSTEM_MAIN_01", "RESEARCH_LOGS", "PROJECT_ALPHA", "SECURE_SANDBOX"]
    if st.session_state.current_chat not in chat_list:
        chat_list.append(st.session_state.current_chat)
        
    st.session_state.current_chat = st.selectbox("ROUTING CHANNEL:", chat_list, index=chat_list.index(st.session_state.current_chat))
    
    st.markdown("<hr style='border:1px solid #FF5500;'>", unsafe_allow_html=True)
    st.markdown("<h3 style='color:#FF5500;'>[Z] MEMORY_LOADER</h3>", unsafe_allow_html=True)
    uploaded_text = st.text_area("INJECT RAW TEXT DATA ARCHIVE SETS:", height=120)
    
    if st.button("🧬 SYNC WITH INFINITE MEMORY") and uploaded_text:
        with st.spinner("COMMITTING ANCHOR VECTOR MATRICES..."):
            try:
                embedding_response = pc_client.inference.embed(
                    model="multilingual-e5-large",
                    inputs=[uploaded_text],
                    parameters={"input_type": "passage"}
                )
                vector_embedding = embedding_response["values"]
                uid = f"doc_{int(time.time())}"
                index.upsert(vectors=[{"id": uid, "values": vector_embedding, "metadata": {"text": uploaded_text, "type": "knowledge"}}])
                st.success("SUCCESS // SYSTEM RETRIEVAL VAULTS LOADED SUCCESSFULLY.")
            except Exception as e:
                st.error(f"MATRIX INGEST FAULT: {str(e)}")

# --- MAIN SCREEN PERMANENT DATABASE RUNTIME STREAM ---
st.markdown(f"<h1>⚡ ACTIVE_STREAM // {st.session_state.current_chat}</h1>", unsafe_allow_html=True)

# RECOVER LOG HISTORY CORES DIRECTLY FROM PINECONE CLOUD STORAGE
chat_history_logs = []
try:
    history_signature = pc_client.inference.embed(
        model="multilingual-e5-large",
        inputs=[f"Fetch chats for channel stream index tracking system values {st.session_state.current_chat}"],
        parameters={"input_type": "query"}
    )
    history_vector = history_signature["values"]
    
    cloud_records = index.query(vector=history_vector, top_k=25, include_metadata=True)
    
    sorted_matches = sorted(
        [m for m in cloud_records['matches'] if 'metadata' in m and m['metadata'].get('type') == 'chat' and m['metadata'].get('channel') == st.session_state.current_chat],
        key=lambda x: x['metadata'].get('timestamp', 0)
    )
    
    for record in sorted_matches:
        chat_history_logs.append({"role": record['metadata']['role'], "content": record['metadata']['text']})
except Exception:
    pass

# Render historical messages
for msg in chat_history_logs:
    if msg["role"] == "user":
        st.markdown(f'<div class="chat-container user-block"><b>[USER_PROMPT] >></b><br>{msg["content"]}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="chat-container ai-block"><b>[CORE_OUTPUT] >></b><br>{msg["content"]}</div>', unsafe_allow_html=True)

def submit_prompt():
    user_query = st.session_state.input_field_key.strip()
    if not user_query:
        return
        
    history_str = ""
    for msg in chat_history_logs:
        role_label = "User" if msg["role"] == "user" else "AI Assistant"
        history_str += role_label + ": " + str(msg["content"]) + "\n"
        
    # Commit user prompt to Pinecone permanently [1.2]
    try:
        user_vec_resp = pc_client.inference.embed(model="multilingual-e5-large", inputs=[user_query], parameters={"input_type": "passage"})
        user_uid = f"chat_user_{int(time.time())}_{int(time.time()*1000)%1000}"
        index.upsert(vectors=[{
            "id": user_uid, 
            "values": user_vec_resp["values"], 
            "metadata": {"text": user_query, "role": "user", "type": "chat", "channel": st.session_state.current_chat, "timestamp": time.time()}
        }])
    except Exception:
        pass
    
    memory_context = "No structural deep memories found."
    web_context = "Live digital systems network arrays unverified."
    ai_output = ""
    
    with st.spinner("ORCHESTRATING CLOUD CONTEXT LOOPS..."):
        try:
            query_response = pc_client.inference.embed(model="multilingual-e5-large", inputs=[user_query], parameters={"input_type": "query"})
            query_vector = query_response["values"]
            memory_results = index.query(vector=query_vector, top_k=5, include_metadata=True)
            memory_context = "\n".join([match['metadata']['text'] for match in memory_results['matches'] if 'metadata' in match and match['metadata'].get('type') == 'knowledge'])
        except Exception:
            pass
            
        try:
            search_results = search_tool.invoke({"query": user_query})
            web_context = str(search_results)
        except Exception:
            pass

        # Clean string joining without using multi-line triple quoted syntax variables
        system_prompt = (
            "You are a highly premium AI core agent operating inside a secure cyber terminal interface.\n"
            "Synthesize context streams and past threads perfectly to answer the objective question.\n\n"
            "[RECENT CONVERSATION HISTORY LOGS]:\n" + history_str + "\n\n"
            "[INFINITE CLOUD RETRIEVAL VECTOR SPACE]:\n" + memory_context + "\n\n"
            "[LIVE WEB NETWORK TARGET DATASTREAM]:\n" + web_context + "\n\n"
            "Current User Question: " + user_query
        )
        
        try:
            response = llm.invoke(system_prompt)
            ai_output = response.content
        except Exception as e:
            ai_output = "HARDWARE TERMINAL DATA LOG EXCEPTION FAULT: " + str(e)
            
        # Commit AI output to Pinecone permanently [1.2]
        try:
            ai_vec_resp = pc_client.inference.embed(model="multilingual-e5-large", inputs=[ai_output], parameters={"input_type": "passage"})
            ai_uid = f"chat_ai_{int(time.time())}_{int(time.time()*1000)%1000}"
