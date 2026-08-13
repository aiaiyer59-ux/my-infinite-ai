import os
import streamlit as st
from langchain_groq import ChatGroq
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_pinecone import PineconeVectorStore
from pinecone import Pinecone

# 1. Page Config
st.set_page_config(page_title="Infinite AI Agent", layout="wide")
st.title("🚀 Free Infinite Context + Live Search AI")

# 2. Check for Hidden Keys
if not os.getenv("GROQ_API_KEY") or not os.getenv("PINECONE_API_KEY") or not os.getenv("TAVILY_API_KEY"):
    st.error("Missing API Keys! Please add them to your Hugging Face Space Settings.")
    st.stop()

# 3. Load the Absolute Best Open-Source Brain (Llama 3.3 70B via Groq)
llm = ChatGroq(
    model="openai/gpt-oss-120b",
    temperature=0.5,
    groq_api_key=os.getenv("GROQ_API_KEY")
)

# 4. Connect to Free Pinecone Cloud (Using the exact integrated setup from your screen)
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
index = pc.Index("infinite-context")

# 5. Load Free Live Search Engine
search_tool = TavilySearchResults(tavily_api_key=os.getenv("TAVILY_API_KEY"), max_results=3)

# --- UI INTERFACE ---
tab1, tab2 = st.tabs(["💬 Chat with AI", "📁 Upload Knowledge Base"])

with tab2:
    st.subheader("Add Data to Infinite Memory")
    uploaded_text = st.text_area("Paste articles, documents, or logs here:")
    if st.button("Save to Cloud Memory") and uploaded_text:
        with st.spinner("Saving data to Pinecone..."):
            # Pinecone handles the embedding automatically based on your dashboard settings
            index.upsert(vectors=[{"id": f"doc_{index.describe_index_stats()['total_vector_count']}", "metadata": {"text": uploaded_text}}])
            st.success("Saved successfully! The AI will remember this forever.")

with tab1:
    user_query = st.text_input("Ask a question (The AI will search memory and the live web automatically):")
    
    if user_query:
        with st.spinner("Analyzing web and memory..."):
            # A. Retrieve data from Infinite Context DB
            try:
                memory_results = index.query(vector=[0]*1024, top_k=3, include_metadata=True)
                memory_context = "\n".join([match['metadata']['text'] for match in memory_results['matches'] if 'metadata' in match])
            except:
                memory_context = "No previous memory found."
            
            # B. Retrieve live data from Web Search
            try:
                search_results = search_tool.invoke({"query": user_query})
                web_context = str(search_results)
            except:
                web_context = "No live web results found."

            # C. Combine everything into one super-prompt
            system_prompt = f"""
            You are a helpful AI assistant. Answer the user's query using the provided Context and Live Web Search.
            
            [Infinite Memory Context]:
            {memory_context}
            
            [Live Web Search Context]:
            {web_context}
            
            User Question: {user_query}
            """
            
            # D. Get answer from the high-end 70B model
            response = llm.invoke(system_prompt)
            st.write("### Answer:")
            st.write(response.content)
