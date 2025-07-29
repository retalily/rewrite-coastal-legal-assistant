
import os
import streamlit as st
import requests
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.document_loaders import TextLoader
from langchain.chat_models import ChatOpenAI
from langchain.chains import RetrievalQA

# === UI Setup ===
st.set_page_config(page_title="EU Coastal Legal Assistant", page_icon="🌊")
st.image("logo.png", width=150)
st.title("⚖️ EU Coastal Legal Assistant (AI-powered)")

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

# === Example Clickable Questions ===
st.markdown("#### 💬 Example Questions")
example_questions = [
    "What legal obligations apply to wetland restoration?",
    "How does the CAP support coastal biodiversity?",
    "What indicators are required under the Nature Restoration Law?",
    "What does the Water Framework Directive say about river rewilding?"
]

selected_question = None
for i, q in enumerate(example_questions):
    if st.button(q, key=f"q_{i}"):
        selected_question = q

query = st.text_input("🔍 Ask a question about EU coastal nature and legal restoration:")

if selected_question:
    query = selected_question
    st.markdown(f"**Selected Question:** _{query}_")

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

# === GPT-3.5 Chat LLM
llm = ChatOpenAI(
    model_name="gpt-3.5-turbo",
    temperature=0.2,
    openai_api_key=st.secrets["openai_key"]
)

qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    retriever=vectordb.as_retriever(search_type="similarity", k=3),
    return_source_documents=True,
    chain_type_kwargs={
        "prompt": (
            "You are an EU legal assistant. Answer the following question ONLY using the provided reference documents. "
            "Do not use external knowledge or speculate. Cite relevant directives or legal clauses if possible."
        )
    }
)

if query:
    with st.spinner("📘 Searching legal documents and preparing an answer..."):
        result = qa_chain({"query": query})
        st.subheader("📘 Answer (based only on uploaded legal texts)")
        st.write(result["result"])

        st.subheader("📎 Sources")
        for doc in result["source_documents"]:
            st.markdown(f"- `{os.path.basename(doc.metadata['source'])}`")
else:
    st.info("💬 Ask a question or click an example to begin.")
