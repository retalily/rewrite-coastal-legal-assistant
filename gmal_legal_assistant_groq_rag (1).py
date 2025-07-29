
import os
import streamlit as st
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import FAISS
from langchain.embeddings import HuggingFaceEmbeddings
from langchain_community.document_loaders import TextLoader
from langchain.llms import OpenAI
from langchain.chains import RetrievalQA
from langchain_community.llms.groq import ChatGroq

# === UI Setup ===
st.set_page_config(page_title="EU Coastal Legal Assistant", page_icon="🌍")
st.image("logo.png", width=150)
st.title("⚖️ EU Coastal Legal Assistant (AI-powered, doc-limited)")

# === Sidebar Directives ===
with st.sidebar:
    st.markdown("### 📚 EU Directives")
    st.markdown("""
- Nature Restoration Regulation (EU) 2024/1991  
- EU Biodiversity Strategy for 2030  
- Habitats Directive (92/43/EEC)  
- Birds Directive (2009/147/EC)  
- Water Framework Directive (2000/60/EC)  
- Marine Strategy Framework Directive (2008/56/EC)  
- Floods Directive (2007/60/EC)  
- Common Agricultural Policy (CAP) (2023–2027)  
- European Climate Law (2021/1119)
    """)

# === Load and index documents from /Text folder ===
@st.cache_resource
def load_vectorstore():
    folder_path = "Text"
    docs = []
    for file in os.listdir(folder_path):
        if file.endswith(".txt"):
            loader = TextLoader(os.path.join(folder_path, file), encoding="utf-8")
            docs.extend(loader.load())

    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    split_docs = splitter.split_documents(docs)

    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    vectordb = FAISS.from_documents(split_docs, embeddings)
    return vectordb

vectordb = load_vectorstore()

# === Define Groq LLM and QA Chain ===
llm = ChatGroq(
    model="llama3-70b-8192",
    api_key=st.secrets["groq_api_key"]
)

qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    retriever=vectordb.as_retriever(search_type="similarity", k=3),
    return_source_documents=True
)

# === Question input ===
st.markdown("#### 💡 Ask a Question")
query = st.text_input("Ask about EU coastal restoration, rewilding law, indicators, or planning:")

if query:
    with st.spinner("🔍 Searching documents and formulating answer..."):
        result = qa_chain({"query": query})
        st.subheader("📘 Answer")
        st.write(result["result"])

        st.subheader("📎 Sources")
        for doc in result["source_documents"]:
            st.markdown(f"- `{os.path.basename(doc.metadata['source'])}`")
else:
    st.info("💬 Ask anything related to EU coastal nature policy and law.")
