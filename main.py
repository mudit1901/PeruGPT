# streamlit_app.py

import streamlit as st
from io import BytesIO
from docx import Document
from services.rfp_generator import generate_rfp
from services.qa_chat_chroma import get_answer_from_query


st.set_page_config(page_title="PeruGPT", layout="centered")

st.title("🧠 PeruGPT")

# Create tabs for different functionalities
tab1, tab2 = st.tabs(["💬 Ask a Question","📄 Generate RFP"])

# Q&A Chat Tab
with tab1:
    st.markdown("## 💬 Ask Anything About Your PDFs")

    # Initialize session state for chat history
    if "qa_history" not in st.session_state:
        st.session_state.qa_history = []

    # Display chat history in bubble layout
    for chat in st.session_state.qa_history:
        # User message (right-aligned)
        col1, col2 = st.columns([1, 5])
        with col2:
            st.markdown(
                f"""
                <div style='text-align: right; background-color: #dcf8c6;
                            padding: 10px; border-radius: 10px;
                            margin-bottom: 5px; margin-left: auto; width: fit-content; max-width: 100%;'>
                    {chat['question']}
                </div>
                """, unsafe_allow_html=True
            )

        # Assistant message (left-aligned)
        col1, col2 = st.columns([5, 1])
        with col1:
            st.markdown(
                f"""
                <div style='text-align: left; background-color: #f1f0f0;
                            padding: 10px; border-radius: 10px;
                            margin-bottom: 20px; width: fit-content; max-width: 100%;'>
                    {chat['answer']}
                </div>
                """, unsafe_allow_html=True
            )

    # Input box fixed at the bottom
    user_question = st.chat_input("Ask about deliverables, scope, timeline, compliance, etc...")

    if user_question:
        # Store user question in chat
        st.session_state.qa_history.append({
            "question": user_question,
            "answer": "⏳ Generating response..."
        })

        st.rerun()

    # Generate and update answer if pending
    if st.session_state.qa_history and st.session_state.qa_history[-1]["answer"] == "⏳ Generating response...":
            latest_q = st.session_state.qa_history[-1]["question"]
            latest_a = get_answer_from_query(latest_q)
            st.session_state.qa_history[-1]["answer"] = latest_a
            st.rerun()

    # Reset button
    if st.button("🔁 Reset Chat"):
        st.session_state.qa_history = []
        st.rerun()