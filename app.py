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

# 2. Cyberpunk Interface Stylesheet
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
    st.error("🚨 CONFIG ERROR: Missing system environment keys.")
    st.stop()

# 4. State Initializers
if "chats" not in st.session_state:
    st.session_state.chats = {"SYSTEM_MAIN_01": []}
if "current_chat" not in st.session_state:
    st.session_state.current_chat = "SYSTEM_MAIN_01"

# 5. Core Engine Assembly
@st.cache_resource
def load_llm():
    return ChatGroq(model="openai/gpt-oss-120b", temperature=0.3, groq_api_key=os.getenv("GROQ_API_KEY"))

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
    st.error(f"❌ CRITICAL FAULT: {str(e)}")
    st.stop()

# 6. Sidebar Control Panel Layout
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

    chat_list = list(st.session_state.chats.keys())
    st.session_state.current_chat = st.selectbox("ROUTING CHANNEL:", chat_list, index=chat_list.index(st.session_state.current_chat))
    
    st.markdown("<hr style='border:1px solid #FF5500;'>", unsafe_allow_html=True)
    st.markdown("<h3 style='color:#FF5500;'>[Z] MEMORY_LOADER</h3>", unsafe_allow_html=True)
    uploaded_text = st.text_area("INJECT RAW TEXT DATA:", height=150)
    
    if st.button("🧬 SYNC WITH INFINITE MEMORY") and uploaded_text:
        with st.spinner("CONVERTING ARCHIVES IN THE CLOUD..."):
            try:
                embedding_response = pc_client.inference.embed(
                    model="multilingual-e5-large",
                    inputs=[uploaded_text],
                    parameters={"input_type": "passage"}
                )
                vector_embedding = embedding_response["values"]
                vector_count = index.describe_index_stats()['total_vector_count']
                index.upsert(vectors=[{"id": f"doc_{vector_count}", "values": vector_embedding, "metadata": {"text": uploaded_text}}])
                st.success("SUCCESS // MATRIX RANGE LOADED INTO MEMORY.")
            except Exception as e:
                st.error(f"UPLOAD FAULT: {str(e)}")

# --- MAIN SCREEN RUNTIME ---
st.markdown(f"<h1>⚡ ACTIVE_STREAM // {st.session_state.current_chat}</h1>", unsafe_allow_html=True)

# Loop and render everything currently saved in active log stream
for msg in st.session_state.chats[st.session_state.current_chat]:
    if msg["role"] == "user":
        st.markdown(f'<div class="chat-container user-block"><b>[USER_PROMPT] >></b><br>{msg["content"]}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="chat-container ai-block"><b>[CORE_OUTPUT] >></b><br>{msg["content"]}</div>', unsafe_allow_html=True)

def submit_prompt():
    user_query = st.session_state.input_field_key.strip()
    if user_query:
        # Formulate active back-and-forth block string data history
        history_str = ""
        for msg in st.session_state.chats[st.session_state.current_chat]:
            role_label = "User" if msg["role"] == "user" else "AI Assistant"
            history_str += f"{role_label}: {msg['content']}\n"
        
        # Append User Entry to Session Log UI immediately
        st.session_state.chats[st.session_state.current_chat].append({"role": "user", "content": user_query})
        
        with st.spinner("READING ARCHIVE SPACE MATRIX VAULTS..."):
            try:
                query_response = pc_client.inference.embed(
                    model="multilingual-e5-large",
                    inputs=[user_query],
                    parameters={"input_type": "query"}
                )
                query_vector = query_response["values"]
                memory_results = index.query(vector=query_vector, top_k=3, include_metadata=True)
                memory_context = "\n".join([match['metadata']['text'] for match in memory_results['matches'] if 'metadata' in match and 'text' in match['metadata']])
            except:
                memory_context = "No memory context mapped."
                
            try:
                search_results = search_tool.invoke({"query": user_query})
                web_context = str(search_results)
            except:
                web_context = "Live search channels unrecoverable."

            # We pass the conversation timeline string straight down to system instructions
            system_prompt = f"""
            You are a highly premium AI core agent operating inside a secure cyber terminal interface.
            Synthesize the context streams and past thread logs perfectly to solve the User Objective question.
            
            [RECENT CONVERSATION HISTORY LOGS]:
            {history_str}
            
            [INFINITE CLOUD RETRIEVAL VECTOR SPACE]:
            {memory_context}
            
            [LIVE WEB NETWORK TARGET DATASTREAM]:
            {web_context}
            
            Current User Question: {user_query}
            """
            
            try:
                response = llm.invoke(system_prompt)
                ai_output = response.content
            except Exception as e:
                ai_output = f"HARDWARE MATRIX FAULT: {str(e)}"
                
            st.session_state.chats[st.session_state.current_chat].append({"role": "ai", "content": ai_output})
            st.session_state.input_field_key = ""

with st.form(key="command_prompt_form", clear_on_submit=True):
    st.text_input("EXECUTE COMMAND PROMPT...", key="input_field_key")
    st.form_submit_button(label="TRANSMIT PROMPT", on_click=submit_prompt)
