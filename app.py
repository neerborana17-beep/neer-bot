import streamlit as st
import requests
import json
import os

# --- 1. API Key (Secrets se uthayenge) ---
API_KEY = st.secrets["OPENROUTER_API_KEY"]

# --- 2. Page Config & CSS (UI Look) ---
st.set_page_config(page_title="Neer AI", page_icon="💬")

st.markdown("""
    <style>
    /* Header को टॉप पर फिक्स करने के लिए */
    [data-testid="stVerticalBlock"] > div:first-child {
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        background-color: #0b141a; /* WhatsApp dark color */
        z-index: 1000;
        padding: 10px 20px;
        border-bottom: 1px solid #202c33;
    }

    /* चैट कंटेंट को हेडर के नीचे से शुरू करने के लिए मार्जिन */
    .stMain {
        margin-top: 80px;
    }

    .header-container { 
        display: flex; 
        align-items: center; 
        gap: 12px; 
    }
    
    .profile-pic { 
        width: 45px; 
        height: 45px; 
        border-radius: 50%; 
        border: 2px solid #00a884; 
        object-fit: cover; 
    }

    .neer-name { 
        color: white; 
        font-size: 20px; 
        font-weight: bold; 
        margin: 0; 
    }

    .online-status { 
        color: #00a884; 
        font-size: 12px; 
        margin: 0; 
    }
    </style>
    """, unsafe_allow_html=True)


# --- 3. Header Display ---
col1, col2 = st.columns([1, 10])
with col1:
    # Agar image file hai toh wo dikhao, varna default icon
    if os.path.exists("neer_dp.png"):
        st.image("neer_dp.png", width=45)
    else:
        st.markdown("👤") 

with col2:
    st.markdown('<p class="neer-name">N E E R</p><p class="online-status">online</p>', unsafe_allow_html=True)

st.divider()

# --- 4. Chat Memory Logic ---
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": "Tera naam Neer hai. Tu smart desi dost hai. Short aur realistic reh. Mood track kar."}]

# Display Messages
for msg in st.session_state.messages[1:]:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# --- 5. User Input & AI Response ---
prompt = st.chat_input("Bolo bhai...")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    with st.chat_message("assistant"):
        with st.spinner("typing..."):
            res = requests.post(
                url="https://openrouter.ai/api/v1/chat/completions",
                headers={"Authorization": f"Bearer {API_KEY}"},
                data=json.dumps({
                    "model": "google/gemini-2.0-flash-001", 
                    "messages": st.session_state.messages,
                    "tools": [{"type": "web_search"}]
                })
            )
            reply = res.json()['choices'][0]['message']['content']
            st.write(reply)
            st.session_state.messages.append({"role": "assistant", "content": reply})
    
