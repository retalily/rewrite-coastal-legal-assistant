
import os
import streamlit as st
import requests

# === Load OpenAI API Key from Secrets ===
OPENAI_API_KEY = st.secrets["openai_key"]

# === UI Setup ===
st.set_page_config(page_title="GMAL Legal Assistant", page_icon="⚖️")
st.image("logo.png", width=150)
st.title("⚖️ GMAL EU Legal Assistant (OpenAI-powered)")

# === Sidebar Directives ===
with st.sidebar:
    st.markdown("### 📚 Directives Commonly Referenced")
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
st.markdown("#### 💡 Example Questions")
example_questions = [
    "What would a rewilded Atlantic coast look like in 2030?",
    "Which EU policies support estuary and saltmarsh restoration?",
    "How can the CAP be used for agri-rewilding and hedgerows?",
    "What are urban greening priorities under GMAL?"
]

selected_question = None
for i, q in enumerate(example_questions):
    if st.button(q, key=f"ex_{i}"):
        selected_question = q

# === Ask User Question ===
query = st.text_input("🔍 Ask a question about coastal rewilding:")

if selected_question:
    query = selected_question
    st.markdown(f"**Selected Question:** _{query}_")

# === Keyword Filter (relaxed but still relevant to rewilding)
def is_relevant(q):
    themes = [
        "coastal", "rewilding", "restoration", "habitat", "wetland", "estuaries", "saltmarsh", "urban nature",
        "biodiversity", "greening", "marine", "floodplain", "seagrass", "river", "ecological", "climate adaptation",
        "pollinators", "tree canopy", "passive rewilding", "marine protected", "resilience", "nature-based solutions"
    ]
    return any(t in q.lower() for t in themes)

# === OpenAI Chat Function ===
def call_openai(question):
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "gpt-3.5-turbo",
        "messages": [
            {"role": "system", "content": (
                "You are an EU legal and ecological assistant helping users understand how EU laws, "
                "policies, and funding streams relate to coastal rewilding. Support scenario planning, "
                "visioning, and multi-policy alignment under GMAL (Green Marine Atlantic Landscapes)."
            )},
            {"role": "user", "content": question}
        ]
    }
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"]
    else:
        return f"❌ Error {response.status_code}: {response.text}"

# === Handle Response ===
if query:
    if not is_relevant(query):
        st.warning("⚠️ This question appears unrelated to coastal rewilding. Please refocus your query.")
    else:
        with st.spinner("💡 Thinking with GPT-3.5..."):
            answer = call_openai(query)
            st.subheader("🧠 Answer")
            st.write(answer)
else:
    st.info("💬 Enter a question or click a suggestion.")
