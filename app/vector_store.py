import streamlit as st
from embedding_client import EmbeddingClient
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.vectorstores.chroma import Chroma
from langchain_core.documents import Document
from pdf_processing import DocumentProcessor
from settings import config


class ChromaCollectionCreator:
    def __init__(self, processor, embed_model):
        """
        Initializes the ChromaCollectionCreator with a DocumentProcessor instance and embeddings configuration.
        :param processor: An instance of DocumentProcessor that has processed documents.
        :param embeddings_config: An embedding client for embedding documents.
        """
        self.processor = processor  # This will hold the DocumentProcessor from Task 3
        self.embed_model = embed_model  # This will hold the EmbeddingClient from Task 4
        self.db = None  # This will hold the Chroma collection

    def create_chroma_collection(self):
        """
        Creates a Chroma collection from the documents processed by the DocumentProcessor instance.
        """

        # Check for processed documents
        if len(self.processor.pages) == 0:
            st.error("No documents found!", icon="🚨")
            return

        # Split documents into text chunks
        text_splitter = CharacterTextSplitter(separator=".", chunk_size=1000, chunk_overlap=100)

        # Split the processed documents into text chunks
        texts = text_splitter.split_documents(self.processor.pages)

        if texts is not None:
            st.success(f"Successfully split pages to {len(texts)} documents!", icon="✅")

        # Create the Chroma Collection
        self.db = Chroma.from_documents(self.processor.pages, self.embed_model)

        # Provide feedback to the user regarding the success of the Chroma collection creation
        if self.db:
            st.success("Successfully created Chroma Collection!", icon="✅")
        else:
            st.error("Failed to create Chroma Collection!", icon="🚨")

    def as_retriever(self):
        # Wrapper method to return the self.db when the call is made by the retriever
        return self.db.as_retriever()

    def query_chroma_collection(self, query) -> Document:
        """
        Queries the created Chroma collection for documents similar to the query.
        :param query: The query string to search for in the Chroma collection.

        Returns the first matching document from the collection with similarity score.
        """
        if self.db:
            docs = self.db.similarity_search_with_relevance_scores(query)
            if docs:
                return docs[0]
            else:
                st.error("No matching documents found!", icon="🚨")
        else:
            st.error("Chroma Collection has not been created!", icon="🚨")


if __name__ == "__main__":
    processor = DocumentProcessor()
    processor.ingest_documents()

    embed_config = {
        "model_name": "textembedding-gecko@003",
        "project": config.PROJECT_ID,
        "location": config.PROJECT_LOCATION,
    }

    embed_client = EmbeddingClient(**embed_config)

    chroma_creator = ChromaCollectionCreator(processor, embed_client)

    with st.form("Load Data to Chroma"):
        st.write("Select PDFs for Ingestion, then click Submit")

        submitted = st.form_submit_button("Submit")
        if submitted:
            chroma_creator.create_chroma_collection()
