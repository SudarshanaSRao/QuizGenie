import streamlit as st
from embedding_client import EmbeddingClient
from pdf_processing import DocumentProcessor
from settings import config
from vector_store import ChromaCollectionCreator

if __name__ == "__main__":
    st.header("Quizzify")

    # Configuration for EmbeddingClient
    embed_config = {
        "model_name": "textembedding-gecko@003",
        "project": config.PROJECT_ID,
        "location": "us-central1",
    }

    screen = st.empty()  # Screen 1, ingest documents
    with screen.container():
        docs = DocumentProcessor()
        processed_data = docs.ingest_documents()
        embed_client = EmbeddingClient(**embed_config)
        chroma_creator = ChromaCollectionCreator(docs, embed_client)

        with st.form("Load Data to Chroma"):
            st.subheader("Quiz Builder")
            st.write("Select PDFs for Ingestion, the topic for the quiz, and click Generate!")

            quiz_topic = st.text_input("Enter the quiz topic:", placeholder="Topic of the Document")
            num_questions = st.slider("Select the number of questions", min_value=1, max_value=20)

            document = None

            submitted = st.form_submit_button("Generate a Quiz!")
            if submitted:
                chroma_creator.create_chroma_collection()
                document = chroma_creator.query_chroma_collection(quiz_topic)

    if document:
        screen.empty()  # Screen 2
        with st.container():
            st.header("Query Chroma for Topic, top Document: ")
            st.write(document)
