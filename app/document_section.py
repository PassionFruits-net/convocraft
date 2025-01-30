import streamlit as st
from utils.document_handler import upload_and_process_document
from utils.vector_store import VectorStore
import numpy as np

def render_document_section():
    with st.sidebar.expander("📚 Document Management", expanded=False):
        if "vector_store" not in st.session_state:
            st.session_state["vector_store"] = VectorStore()

        chunks = upload_and_process_document()

        if chunks and st.button("Process Document"):
            with st.spinner("Processing document..."):
                try:
                    st.session_state["vector_store"].create_index(chunks)
                    st.success("Document processed and indexed successfully!")
                except Exception as e:
                    st.error(f"Error processing document: {e}")
                    st.error(f"Error type: {type(e)}")
                    import traceback
                    st.error(f"Full error: {traceback.format_exc()}")

        if "document_chunks" in st.session_state:
            st.write(f"Number of chunks processed: {len(st.session_state['document_chunks'])}")