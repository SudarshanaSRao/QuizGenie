import os
import tempfile
import uuid

import streamlit as st
from langchain_community.document_loaders import PyPDFLoader


class DocumentProcessor:
    """
    This class encapsulates the functionality for processing uploaded PDF documents using Streamlit
    and Langchain's PyPDFLoader. It provides a method to render a file uploader widget, process the
    uploaded PDF files, extract their pages, and display the total number of pages extracted.
    """

    def __init__(self):
        self.pages = []  # List to keep track of pages from all documents

    def ingest_documents(self):
        """
        Renders a file uploader in a Streamlit app, processes uploaded PDF files,
        extracts their pages, and updates the self.pages list with the total number of pages.
        """

        # Render a file uploader widget
        uploaded_files = st.file_uploader(
            label="Choose PDF file",
            type=["pdf"],
            accept_multiple_files=True,
        )

        if uploaded_files is not None:
            for uploaded_file in uploaded_files:
                # Generate a unique identifier to append to the file's original name
                unique_id = uuid.uuid4().hex
                original_name, file_extension = os.path.splitext(uploaded_file.name)
                temp_file_name = f"{original_name}_{unique_id}{file_extension}"
                temp_file_path = os.path.join(tempfile.gettempdir(), temp_file_name)

                # Write the uploaded PDF to a temporary file
                with open(temp_file_path, "wb") as f:
                    f.write(uploaded_file.getvalue())

                # Process the temporary file
                loader = PyPDFLoader(temp_file_path)

                # Add the extracted pages to the 'pages' list.
                self.pages.extend(loader.load())

                # Clean up by deleting the temporary file.
                os.unlink(temp_file_path)

            # Display the total number of pages processed.
            st.write(f"Total pages processed: {len(self.pages)}")


if __name__ == "__main__":
    processor = DocumentProcessor()
    processor.ingest_documents()
