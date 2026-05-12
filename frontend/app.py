import streamlit as st
import requests
import os
from frontend.components.cards import render_assessment_card

# Default API URL
API_URL = os.environ.get("API_URL", "http://localhost:8000")

st.set_page_config(
    page_title="SHL Assessment Recommender",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for aesthetics
st.markdown("""
<style>
    .stApp {
        background-color: #f8f9fa;
    }
    .chat-container {
        padding: 20px;
        background: white;
        border-radius: 12px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
    }
</style>
""", unsafe_allow_html=True)

st.title("💼 SHL Assessment Recommender")
st.markdown("Find the right SHL assessments for your hiring needs through conversation.")

# Sidebar
with st.sidebar:
    st.header("Settings")
    if st.button("Reset Conversation", type="primary"):
        st.session_state.messages = []
        st.rerun()
    st.markdown("---")
    st.markdown("### About")
    st.markdown("This agent helps you find SHL Individual Test Solutions. It asks clarification questions, recommends assessments, and can compare them.")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        # If assistant has recommendations, display them
        if message["role"] == "assistant" and message.get("recommendations"):
            for rec in message["recommendations"]:
                render_assessment_card(rec)

# React to user input
if prompt := st.chat_input("E.g., I'm hiring a Senior Java Developer..."):
    # Display user message in chat message container
    st.chat_message("user").markdown(prompt)
    
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Prepare payload for API
    # We only send role and content to the backend
    payload = {
        "messages": [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]
    }

    # Call Backend API
    with st.spinner("Agent is thinking..."):
        try:
            response = requests.post(f"{API_URL}/chat", json=payload)
            response.raise_for_status()
            data = response.json()
            
            reply = data.get("reply", "")
            recommendations = data.get("recommendations", [])
            
            # Display assistant response
            with st.chat_message("assistant"):
                st.markdown(reply)
                if recommendations:
                    for rec in recommendations:
                        render_assessment_card(rec)
            
            # Add assistant response to chat history
            st.session_state.messages.append({
                "role": "assistant", 
                "content": reply,
                "recommendations": recommendations
            })
            
        except requests.exceptions.RequestException as e:
            st.error(f"Error communicating with backend API: {e}")
            st.info("Make sure the backend is running at " + API_URL)
