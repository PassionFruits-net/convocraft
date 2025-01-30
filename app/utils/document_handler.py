import streamlit as st
from PyPDF2 import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter

def upload_and_process_document():
    """
    Handles document upload and preprocessing.
    """
    uploaded_file = st.file_uploader("Upload a Document (PDF or Text)", type=["pdf", "txt"])
    if uploaded_file:
        if uploaded_file.name.endswith('.pdf'):
            reader = PdfReader(uploaded_file)
            text = "\n".join([page.extract_text() for page in reader.pages])
        elif uploaded_file.name.endswith('.txt'):
            text = uploaded_file.read().decode('utf-8')
        else:
            st.error("Unsupported file format.")
            return None

        splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
        chunks = splitter.split_text(text)

        st.session_state['document_chunks'] = chunks
        st.success(f"Document uploaded and split into {len(chunks)} chunks.")
        return chunks

    return None
