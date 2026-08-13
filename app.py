import os
import streamlit as st
from langchain_groq import ChatGroq
from langchain_community.tools.tavily_search import TavilySearchResults
from pinecone import Pinecone

# 1. Page Configuration
st.set_page_config(
    page_title="NEON CORE // AI", 
    page_icon="⚡", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

# 2. Re-designed Cyberpunk Interface Stylesheet (Black, Orange, Red, Neon Green)
st.markdown("""
    <style>
        /* Base Canvas - Deep Cyberpunk Void Black */
        .stApp { 
            background-color: #000000 !important; 
            color: #00FF66 !important; 
            font-family: 'Courier New', monospace;
        }
        
        /* Sidebar Restyling */
        section[data-testid="stSidebar"] { 
            background-color: #050505 !important; 
            border-right: 2px solid #FF5500 !important; 
        }
        
        /* Headers */
        h1, h2, h3, .sidebar-header { 
            color: #FF1100 !important; 
            text-transform: uppercase; 
            letter-spacing: 2px;
            font-weight: 900;
            text-shadow: 0px 0px 8px #FF1100;
        }
        
        /* Custom Message Container Flow Layout */
        .chat-container {
            margin: 15px 0px;
            padding: 15px;
            border-radius: 4px;
            width: 100%;
            clear: both;
        }
        
        /* User Prompt Layout - Vibrant Cyberpunk Orange Accent */
        .user-block {
            background-color: #0a0400;
            border: 1px solid #FF5500;
            border-left: 5px solid #FF5500;
            color: #FFBB00;
            box-shadow: 0px 0px 5px #FF5500;
        }
        
        /* Machine Output Layout - Electric Neon Green Accent */
        .ai-block {
            background-color: #000a03;
            border: 1px solid #00FF66;
            border-left: 5px solid #00FF66;
            color: #33FF77;
            box-shadow: 0px 0px 5px #00FF66;
        }
        
        /* Universal Form Fields (Inputs, Sliders, Dropdowns) */
        .stTextInput>div>div>input, .stTextArea>div>div>textarea, select {
            background-color: #080808 !important;
            color: #00FF66 !important;
            border: 1px solid #FF5500 !important;
            border-radius: 0px !important;
        }
        .stTextInput>div>div>input:focus, .stTextArea>div>div>textarea:focus {
            border: 1px solid #00FF66 !important;
            box-shadow: 0px 0px 10px #00FF66 !important;
        }
        
        /* High Contrast UI Action Elements */
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
            border: 1px solid #00FF66 !important;
            box-shadow: 0px 0px 12px #00FF66;
        }
    </style>
""", unsafe_allow_html=True)

# 3. Secure Environmental Integrity Verification Loop
if not os.getenv("GROQ_API_KEY") or not os.getenv("PINECONE_API_KEY") or not os.getenv("TAVILY_API_KEY"):
    st.error("🚨 CRITICAL FAULT: ENV KEYS NOT DETECTED IN STORAGE RUNTIME HOST.")
    st.stop()

# 4. Multi-Instance Workspace Cache Infrastructure
if "chats" not in st.session_state:
    st.session_state.chats = {"SYSTEM_MAIN_01": []}
if "current_chat" not in st.session_state:
    st.session_state.current_chat = "SYSTEM_MAIN_01"

# 5. Core Control Panel Sidebar Build (Left Anchor)
with st.sidebar:
    st.markdown('<div class="sidebar-header">⚡ NEON CORE // ENGINE</div>', unsafe_allow_html=True)
    
    st.markdown("<h3 style='color:#FF5500;'>[X] MATRIX_CHANNELS</h3>", unsafe_allow_html=True)
    new_chat_name = st.text_input("INITIALIZE NEW STREAM:", placeholder="SECURE_LOG_X...")
    if st.button("⚡ EXECUTE CREATION") and new_chat_name:
        clean_name = new_chat_name.upper().replace(" ", "_")
        if clean_name not in st.session_state.chats:
            st.session_state.chats[clean_name] = []
            st.session_state.current_chat = clean_name
            st.rerun()

    # Active Stream Context Router Selection
    chat_list = list(st.session_state.chats.keys())
    st.session_state.current_chat = st.selectbox(
        "ROUTING CHANNEL TARGET:", 
        chat_list, 
        index=chat_list.index(st.session_state.current_chat)
    )
    
    st.markdown("<hr style='border:1px solid #FF5500;'>", unsafe_allow_html=True)
    
    # Model Tuning Panel
    st.markdown("<h3 style='color:#FF5500;'>[Y] BRAIN_TUNING</h3>", unsafe_allow_html=True)
    ai_creativity = st.slider("VARIANCE LEVEL (TEMP):", min_value=0.0, max_value=1.0, value=0.3, step=0.1)
    
    st.markdown("<hr style='border:1px solid #FF5500;'>", unsafe_allow_html=True)
    
    # Memory Sync Node Zone
    st.markdown("<h3 style='color:#FF5500;'>[Z] MEMORY_LOADER</h3>", unsafe_allow_html=True)
    uploaded_text = st.text_area("INJECT RAW TEXT DOCUMENT ARRAYS:", height=120)
    if st.button("🧬 SYNC WITH INFINITE MEMORY VAULT") and uploaded_text:
        with st.spinner("COMMITTING VECTOR BLOCKS TO PINECONE CLOUD..."):
            try:
                pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
                index = pc.Index("infinite-context")
                vector_count = index.describe_index_stats()['total_vector_count']
                index.upsert(vectors=[{"id": f"doc_{vector_count}", "values": [0.0]*1024, "metadata": {"text": uploaded_text}}])
                st.success("SUCCESS // TARGET VECTOR RANGE SYNCHRONIZED FOREVER.")
            except Exception as e:
                st.error(f"FAIL // PIPELINE VECTOR DROP REJECTED: {str(e)}")

# 6. Global Variable Engine Mapping
@st.cache_resource
def init_engines():
    llm_instance = ChatGroq(model="openai/gpt-oss-120b", temperature=ai_creativity, groq_api_key=os.getenv("GROQ_API_KEY"))
    pc_instance = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
    index_instance = pc_instance.Index("infinite-context")
    search_instance = TavilySearchResults(tavily_api_key=os.getenv("TAVILY_API_KEY"), max_results=3)
    return llm_instance, index_instance, search_instance

try:
    llm, index, search_tool = init_engines()
except Exception as e:
    st.error("CRITICAL EXCEPTION: BACKEND CORE HARDWARE AUTHENTICATION REJECTED.")
    st.stop()

# --- CHAT INTERFACE DISPLAY TIMELINE ---
st.markdown(f"<h1>⚡ ACTIVE_STREAM // {st.session_state.current_chat}</h1>", unsafe_allow_html=True)

# Map UI State Tracking Sessions
active_messages = st.session_state.chats[st.session_state.current_chat]
for msg in active_messages:
    if msg["role"] == "user":
        st.markdown(f'<div class="chat-container user-block"><b>[USER_PROMPT] >></b><br>{msg["content"]}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="chat-container ai-block"><b>[CORE_OUTPUT] >></b><br>{msg["content"]}</div>', unsafe_allow_html=True)

# Layout Separator Spacing Fix
st.markdown('<div style="clear:both; margin-bottom:50px;"></div>', unsafe_allow_html=True)

# Input Command line deck bar
user_query = st.text_input("EXECUTE COMMAND PROMPT...", placeholder="Input matrix parameters or run semantic archive lookups...", key="terminal_input")

if user_query:
    st.session_state.chats[st.session_state.current_chat].append({"role": "user", "content": user_query})
    
    with st.spinner("PULLING MEMORY VAULTS AND SCANNING EXTERNAL WEB STRANDS..."):
        # Step A: Infinite Context DB Scraping
        try:
            memory_results = index.query(vector=[0.0]*1024, top_k=3, include_metadata=True)
            memory_context = "\n".join([match['metadata']['text'] for match in memory_results['matches'] if 'metadata' in match and 'text' in match['metadata']])
        except:
            memory_context = "Empty database context records."
        
        # Step B: Live Search Engine Deployment
        try:
            search_results = search_tool.invoke({"query": user_query})
            web_context = str(search_results)
        except:
            web_context = "External live networks unrecoverable."

        # Step C: Heavy Orchestrated Model System Instruction Setup
        system_prompt = f"""
        You are a highly premium AI core agent operating inside a secure cyber terminal terminal interface. 
        Synthesize the dataset context streams perfectly to solve the User Objective question.
        
        [INFINITE CLOUD RETRIEVAL VECTOR SPACE]:
        {memory_context}
        
        [LIVE WEB NETWORK TARGET DATASTREAM]:
        {web_context}
        
        User Objective Question: {user_query}
        """
        
        # Step D: Pull output from custom GPT-OSS 120B model
        try:
            response = llm.invoke(system_prompt)
            ai_output = response.content
        except Exception as e:
            ai_output = f"HARDWARE TERMINAL EXECUTION ERROR: {str(e)}"
        
        st.session_state.chats[st.session_state.current_chat].append({"role": "ai", "content": ai_output})
        st.rerun()

