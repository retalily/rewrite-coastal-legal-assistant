
import os
import streamlit as st
import requests

# === Load Together API Key from Secrets ===
TOGETHER_API_KEY = st.secrets["together_api_key"]

# === UI Setup ===
st.set_page_config(page_title="GMAL Legal Assistant", page_icon="⚖️")
st.image("logo.png", width=150)
st.title("⚖️ GMAL EU Legal Assistant (DeepSeek via Together.ai)")

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
    "How does CAP support agro-ecological restoration?",
    "What urban rewilding goals align with the EU Biodiversity Strategy?",
    "What indicators support marine restoration under MSFD?"
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

# === Keyword Filter (relaxed coastal rewilding scope)
def is_relevant(q):
    keywords = [
        "rewilding", "coastal", "restoration", "nature", "wetland", "habitat",
        "saltmarsh", "marine", "green", "estuaries", "ecosystem", "resilience",
        "climate", "cap", "greening", "passive", "floodplain", "urban nature"
    ]
    return any(k in q.lower() for k in keywords)

# === DeepSeek via Together.ai Chat Function ===
def call_together_api(question):
    url = "https://api.together.xyz/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {TOGETHER_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "deepseek-ai/deepseek-llm-7b-instruct",
        "messages": [
            {"role": "system", "content": (
                "You are an EU legal and ecological advisor supporting GMAL. Provide answers focused on restoration, "
                "rewilding, policy alignment, and scenario-based implementation of coastal and marine EU frameworks."
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
        st.warning("⚠️ This doesn't appear to relate to coastal rewilding. Try focusing on nature, law, or marine policy.")
    else:
        with st.spinner("💬 Thinking with DeepSeek..."):
            response = call_together_api(query)
            st.subheader("🧠 Answer")
            st.write(response)
else:
    st.info("💬 Enter a question or click a suggestion.")
