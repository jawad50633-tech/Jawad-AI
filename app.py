import os
import json
import streamlit as st
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")

# Use Streamlit secrets if .env is not available
if not api_key:
    api_key = st.secrets.get("GROQ_API_KEY")

if not api_key:
    st.error("GROQ_API_KEY is missing.")
    st.stop()

client = Groq(api_key=api_key)
# =========================

# Load Environment Variables
# =========================

# =========================
# Page Config
# =========================
st.set_page_config(
    page_title="My Personal AI",
    page_icon="🧠",
    layout="wide"
)

st.title("🧠 Jawad's AI Assistant")

# =========================
# Session State
# =========================
if "messages" not in st.session_state:
    st.session_state.messages = []

# =========================
# Sidebar
# =========================
with st.sidebar:
    st.header("⚙ Assistant Settings")

    system_prompt = st.text_area(
        "System Prompt",
        value="You are a helpful and highly knowledgeable personal assistant.",
        height=150
    )

    model = st.selectbox(
        "Model",
        [
            "llama-3.3-70b-versatile",
            "llama-3.1-8b-instant",
            "gemma2-9b-it"
        ]
    )

    temperature = st.slider(
        "Temperature",
        min_value=0.0,
        max_value=2.0,
        value=0.7,
        step=0.1
    )

    max_tokens = st.slider(
        "Max Tokens",
        min_value=128,
        max_value=4096,
        value=1024,
        step=128
    )

    history_limit = st.slider(
        "Conversation Memory",
        min_value=2,
        max_value=30,
        value=10
    )

    st.divider()

    if st.button("🗑 Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    st.download_button(
        "📥 Download Chat",
        data=json.dumps(st.session_state.messages, indent=4),
        file_name="chat_history.json",
        mime="application/json",
        use_container_width=True
    )

# =========================
# Display Chat History
# =========================
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# =========================
# Chat Input
# =========================
user_query = st.chat_input("Ask me anything...")

if user_query:

    # Save user message
    st.session_state.messages.append(
        {
            "role": "user",
            "content": user_query
        }
    )

    # Display user message
    with st.chat_message("user"):
        st.markdown(user_query)

    # Assistant response
    with st.chat_message("assistant"):

        placeholder = st.empty()

        try:

            history = st.session_state.messages[-history_limit:]

            messages = [
                {
                    "role": "system",
                    "content": system_prompt
                }
            ]

            messages.extend(history)

            stream = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_completion_tokens=max_tokens,
                stream=True
            )

            assistant_response = ""

            for chunk in stream:

                delta = chunk.choices[0].delta.content

                if delta:
                    assistant_response += delta
                    placeholder.markdown(assistant_response + "▌")

            placeholder.markdown(assistant_response)

        except Exception as e:

            assistant_response = f"❌ Error:\n\n{str(e)}"
            placeholder.error(assistant_response)

    # Save assistant response
    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": assistant_response
        }
    )
