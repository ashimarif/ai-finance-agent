import os
import streamlit as st
import requests
import uuid

# Read from environment variable with fallback to localhost
API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")

# Page configuration
st.set_page_config(
    page_title="Smart Finance & Bill-Split AI Agent",
    page_icon="💸",
    layout="wide"
)

# -------------------------------------------------------------
# SESSION STATE INITIALIZATION
# -------------------------------------------------------------
# Generate or maintain a unique thread_id for conversation memory
if "thread_id" not in st.session_state:
    st.session_state.thread_id = f"session_{uuid.uuid4().hex[:8]}"

# Store chat message history for the UI
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "👋 Hi! I'm your AI Finance & Bill-Splitting Assistant.\n\nTell me your solo expenses (e.g., *'Spent $15 on lunch'*) or group outings (e.g., *'Paid $90 for dinner with Alex and Ben, split evenly'*)."
        }
    ]

# -------------------------------------------------------------
# SIDEBAR CONTROLS & INFO
# -------------------------------------------------------------
with st.sidebar:
    st.title("⚙️ Session Controls")
    st.caption(f"**Thread ID:** `{st.session_state.thread_id}`")
    
    # Check Backend Status
    try:
        health_resp = requests.get(f"{API_BASE_URL}/health", timeout=2)
        if health_resp.status_code == 200:
            st.success("🟢 Backend API: Online")
        else:
            st.warning("🟡 Backend API: Warning")
    except requests.exceptions.RequestException:
        st.error("🔴 Backend API: Offline (Make sure FastAPI is running on port 8000)")

    st.markdown("---")
    st.subheader("💡 Example Queries")
    st.markdown("""
    - **Solo:** `Spent $45 on groceries and $20 on gas`
    - **Split:** `I paid $120 for BBQ with Sarah and John. Split it 3 ways.`
    - **Debts:** `Who owes me money and what is the total?`
    - **Settle:** `Sarah paid me back for everything.`
    - **Summary:** `How much have I spent on food?`
    """)

    st.markdown("---")
    if st.button("🔄 Reset Conversation", use_container_width=True):
        st.session_state.thread_id = f"session_{uuid.uuid4().hex[:8]}"
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": "Conversation reset! How can I assist you with your expenses today?"
            }
        ]
        st.rerun()

# -------------------------------------------------------------
# MAIN CHAT INTERFACE
# -------------------------------------------------------------
st.title("💸 Smart Personal Finance & Bill-Split Assistant")
st.caption("Powered by LangGraph, Gemini 2.0 Flash, FastAPI & PostgreSQL")

# Display previous messages from session history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# User Chat Input Box
user_query = st.chat_input("Log an expense, split a bill, or check IOUs...")

if user_query:
    # 1. Display and record user message
    st.session_state.messages.append({"role": "user", "content": user_query})
    with st.chat_message("user"):
        st.markdown(user_query)

    # 2. Call FastAPI backend
    with st.chat_message("assistant"):
        with st.spinner("Analyzing & updating PostgreSQL database..."):
            try:
                payload = {
                    "thread_id": st.session_state.thread_id,
                    "message": user_query
                }
                response = requests.post(f"{API_BASE_URL}/chat", json=payload, timeout=30)
                
                if response.status_code == 200:
                    api_data = response.json()
                    bot_reply = api_data.get("response", "No response received.")
                else:
                    bot_reply = f"⚠️ Server Error ({response.status_code}): {response.text}"
            except requests.exceptions.ConnectionError:
                bot_reply = "❌ Error: Could not connect to FastAPI backend at `http://127.0.0.1:8000`. Ensure your backend server is running."
            except Exception as e:
                bot_reply = f"❌ An unexpected error occurred: {str(e)}"

            st.markdown(bot_reply)
            st.session_state.messages.append({"role": "assistant", "content": bot_reply})