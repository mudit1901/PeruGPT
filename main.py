# streamlit_app.py

import streamlit as st
from io import BytesIO
from docx import Document
from services.rfp_generator import generate_rfp
from services.qa_chat import get_answer_from_query 

st.set_page_config(page_title="PeruGPT", layout="centered")

st.title("🧠 PeruGPT")

# Create tabs for different functionalities
tab1, tab2 = st.tabs(["💬 Ask a Question","📄 Generate RFP"])

# Q&A Chat Tab
with tab1:
    st.header("💬 Ask Anything")

    user_question = st.text_input("Your question:", placeholder="e.g., What are the main features of the Projects?")

    if st.button("Ask"):
        if user_question.strip():
            with st.spinner("Searching and answering..."):
                response = get_answer_from_query(user_question)
                st.success("🧠 Answer:")
                st.write(response)
        else:
            st.warning("Please enter a question.")

# RFP Generation Tab
with tab2:
    st.header("📄 Generate Request For Proposal")

    requirement = st.text_area("Enter Requirement", height=150, placeholder="e.g., AI-based resume screening system for HR...")

    if st.button("Generate RFP"):
        if requirement.strip():
            with st.spinner("Generating RFP..."):
                rfp_text = generate_rfp(requirement)

            
                st.markdown("### 📃 Generated RFP")
                st.markdown(rfp_text, unsafe_allow_html=False)

                # Save to Word in memory
                buffer = BytesIO()
                doc = Document()
                for para in rfp_text.split('\n'):
                    doc.add_paragraph(para)
                doc.save(buffer)
                buffer.seek(0)

                st.download_button(
                    label="⬇️ Download RFP as .docx",
                    data=buffer,
                    file_name="Generated_RFP.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                )
        else:
            st.warning("Please enter a requirement.")


