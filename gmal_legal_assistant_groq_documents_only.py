
import os
import streamlit as st
import requests

# === Load Groq API Key from Secrets ===
GROQ_API_KEY = st.secrets["groq_api_key"]

# === Load Reference Texts ===
def load_documents():
    folder = "Text"
    content = ""
    for file in os.listdir(folder):
        if file.endswith(".txt"):
            with open(os.path.join(folder, file), "r", encoding="utf-8") as f:
                content += f"\n---\n{f.name}\n" + f.read() + "\n"
    return content.strip()

DOCUMENTS_CONTEXT = load_documents()

# === UI Setup ===
st.set_page_config(page_title="GMAL Assistant – Nature & Policy", page_icon="🌍")
st.image("logo.png", width=150)
st.title("🌿 GMAL Nature & Rewilding Assistant (Groq-powered)")

# === Sidebar Information ===
with st.sidebar:
    st.markdown("### 🌐 Supported Topics")
    st.markdown("""
- Coastal & marine rewilding  
- Ecological restoration & policy  
- Scenario planning & visioning  
- Green infrastructure & adaptation  
- Biodiversity, connectivity, wetlands  
- Climate-resilient land/seascapes  
- Urban rewilding and nature access  
- EU legal, voluntary, and planning instruments  
- Cross-scale coastal strategy thinking  
    """)

# === Clickable Example Questions ===
st.markdown("#### 💡 Ask a Big Vision Question")
example_questions = [
    "What would a rewilded European coastline look like in 2040?",
    "How can cities integrate blue-green coastal infrastructure?",
    "What are indicators of successful estuarine restoration?",
    "How does coastal rewilding improve climate resilience?",
    "What future scenarios are possible for European wetlands?"
]

selected_question = None
for i, q in enumerate(example_questions):
    if st.button(q, key=f"q_{i}"):
        selected_question = q

# === Text Input
query = st.text_input("🔍 Ask about nature futures, planning, and restoration:")

if selected_question:
    query = selected_question
    st.markdown(f"**Selected Question:** _{query}_")

# === Relevance Filter
def is_relevant(q):
    terms = [
        "rewilding", "restoration", "coastal", "landscape", "marine", "vision", "planning",
        "biodiversity", "floodplain", "wetland", "nature", "ecosystem", "climate", "connectivity",
        "saltmarsh", "estuaries", "pollinators", "green infrastructure", "river", "estuaries"
    ]
    return any(t in q.lower() for t in terms)

# === Groq Chat Function (context-restricted)
def call_groq_with_context(question):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "llama3-70b-8192",
        "messages": [
            {"role": "system", "content": (
                "You are a coastal rewilding and ecological advisor for the Green Marine Atlantic Landscapes (GMAL) initiative. "
                "You must only answer questions using the content provided below. Do not invent or summarize beyond this context. "
                "Use relevant parts of the documents to explain concepts or give examples."
            )},
            {"role": "system", "content": f"Reference Documents:\n{DOCUMENTS_CONTEXT}"},
            {"role": "user", "content": question}
        ]
    }
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"]
    else:
        return f"❌ Error {response.status_code}: {response.text}"

# === Handle Response
if query:
    if not is_relevant(query):
        st.warning("⚠️ This may fall outside coastal rewilding themes. Please refine your question.")
    else:
        with st.spinner("📚 Searching the GMAL reference documents..."):
            result = call_groq_with_context(query)
            st.subheader("📘 Answer (from documents only)")
            st.write(result)
else:
    st.info("💬 Ask about restoration, visioning, or policy based only on GMAL docs.")
