import os
import streamlit as st
from langchain_groq import ChatGroq
from langchain_community.tools.tavily_search import TavilySearchResults
from pinecone import Pinecone

# 1. Page Config (Sets clean, wide, modern layout)
st.set_page_config(page_title="AI Studio", page_icon="✨", layout="wide", initial_sidebar_state="expanded")

# --- Custom Google AI Style CSS ---
st.markdown("""
    <style>
        /* Modern font and subtle background styling */
        .stApp { background-color: #0f1115; color: #e3e2e6; }
        /* Clean Chat Bubble Styles */
        .user-bubble {
            background-color: #2b2d31; padding: 14px 18px; 
            border-radius: 20px 20px 4px 20px; margin: 10px 0;
            display: inline-block; max-width: 80%; float: right; clear: both;
        }
        .ai-bubble {
            background-color: #1e1f24; padding: 14px 18px; 
            border-radius: 20px 20px 20px 4px; margin: 10px 0;
            display: inline-block; max-width: 85%; float: left; clear: both;
            border-left: 3px solid #4285f4;
        }
        /* Sidebar Styling */
        section[data-testid="stSidebar"] { background-color: #13151a !important; border-right: 1px solid #23272e; }
        .sidebar-header { font-size: 20px; font-weight: bold; color: #4285f4; margin-bottom: 20px; }
        /* Action buttons styling */
        .stButton>button { border-radius: 20px; background-color: #4285f4; color: white; border: none; }
        .stButton>button:hover { background-color: #3572cd; color: white; }
    </style>
""", unsafe_allow_html=True)

# 2. Check for System API Credentials
if not os.getenv("GROQ_API_KEY") or not os.getenv("PINECONE_API_KEY") or not os.getenv("TAVILY_API_KEY"):
    st.error("🔑 API Keys Missing! Add them to your Streamlit App Advanced Secrets.")
    st.stop()

# 3. Handle Session State Memory for Multiple Chat Windows
if "chats" not in st.session_state:
    st.session_state.chats = {"Chat Window 1": []}
if "current_chat" not in st.session_state:
    st.session_state.current_chat = "Chat Window 1"

# 4. Sidebar Infrastructure (Navigation & Settings Hub)
with st.sidebar:
    st.markdown('<div class="sidebar-header">✨ AI Studio</div>', unsafe_html=True)
    
    # Feature A: Multiple Chat Windows Management
    st.subheader("💬 Active Conversations")
    new_chat_name = st.text_input("New Conversation Name:", placeholder="Project Alpha...")
    if st.button("➕ Create New Chat") and new_chat_name:
        if new_chat_name not in st.session_state.chats:
            st.session_state.chats[new_chat_name] = []
            st.session_state.current_chat = new_chat_name
            st.rerun()

    # Chat Selector Dropdown List
    chat_list = list(st.session_state.chats.keys())
    st.session_state.current_chat = st.selectbox("Switch Active Chat:", chat_list, index=chat_list.index(st.session_state.current_chat))
    
    st.markdown("---")
    
    # Feature B: Creative Engine Parameters slider controls
    st.subheader("⚙️ Model Tuning")
    ai_creativity = st.slider("Creativity Level (Temperature):", min_value=0.0, max_value=1.0, value=0.3, step=0.1)
    
    st.markdown("---")
    
    # Feature C: Embedded Infinite Context Manager (Knowledge Base Sync)
    st.subheader("📁 Upload Knowledge Base")
    uploaded_text = st.text_area("Paste reference data, notes, or documentation text here:", height=150)
    if st.button("💾 Sync to Infinite Cloud Memory") and uploaded_text:
        with st.spinner("Indexing into Pinecone..."):
            try:
                pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
                index = pc.Index("infinite-context")
                vector_count = index.describe_index_stats()['total_vector_count']
                index.upsert(vectors=[{"id": f"doc_{vector_count}", "values": [0.0]*1024, "metadata": {"text": uploaded_text}}])
                st.success("Successfully learned! This context is preserved forever.")
            except Exception as e:
                st.error(f"Pinecone upload failed: {str(e)}")

# 5. Core AI Engines Core Init
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
    st.error("Failed to connect to backend engine models. Double-check secret token variables.")
    st.stop()

# --- MAIN CHAT INTERFACE ---
st.markdown(f"### 🌐 Core Engine: `{st.session_state.current_chat}`")

# Display Past Messages for selected window
active_messages = st.session_state.chats[st.session_state.current_chat]
for msg in active_messages:
    if msg["role"] == "user":
        st.markdown(f'<div class="user-bubble"><b>You:</b><br>{msg["content"]}</div>', unsafe_html=True)
    else:
        st.markdown(f'<div class="ai-bubble"><b>AI Studio:</b><br>{msg["content"]}</div>', unsafe_html=True)

# Spacing container clear floating elements
st.markdown('<div style="clear:both; margin-bottom:100px;"></div>', unsafe_html=True)

# Google AI Floating Bottom Input Form Layout
with st.container():
    user_query = st.text_input("Message AI Studio...", placeholder="Ask a question, analyze vector archives, or search the web...", key="chat_input_field")
    
    if user_query:
        # Append User Entry to Session Log UI
        st.session_state.chats[st.session_state.current_chat].append({"role": "user", "content": user_query})
        
        with st.spinner("Processing deep memory contextual loops..."):
            # Step A: Check Infinite Vector Space Archive Layouts
            try:
                memory_results = index.query(vector=[0.0]*1024, top_k=3, include_metadata=True)
                memory_context = "\n".join([match['metadata']['text'] for match in memory_results['matches'] if 'metadata' in match and 'text' in match['metadata']])
            except:
                memory_context = "No previous context match logged."
            
            # Step B: Live Network Scan Loop Tracking
            try:
                search_results = search_tool.invoke({"query": user_query})
                web_context = str(search_results)
            except:
                web_context = "No structural web documents recovered."

            # Step C: Heavy Orchestrated Model System Instruction Setup
            system_prompt = f"""
            You are a premium AI agent. Analyze user queries using the context sets.
            
            [Infinite Cloud Storage Context]:
            {memory_context}
            
            [Real-time Web Search Data]:
            {web_context}
            
            User Objective Question: {user_query}
            """
            
            # Step D: Pull output from custom GPT-OSS architecture tier
            try:
                response = llm.invoke(system_prompt)
                ai_output = response.content
            except Exception as e:
                ai_output = f"Model Processing Error: {str(e)}"
            
            # Append Response to current chat session record
            st.session_state.chats[st.session_state.current_chat].append({"role": "ai", "content": ai_output})
            st.rerun()

