import streamlit as st
from task_4 import EmbeddingClient
import os
from dotenv import load_dotenv

load_dotenv()
PROJECT_ID = os.environ["PROJECT_ID"]

# Initialize the EmbeddingClient with the provided parameters
model_name = "textembedding-gecko@003"
project = PROJECT_ID
location = "us-central1"
embedding_client = EmbeddingClient(model_name, project, location)

# Get the embedding for "Hello World!"
vectors = embedding_client.embed_query("Hello World!")

# Display the vectors
if vectors:
    st.write("Embedding for 'Hello World!':")
    st.write(vectors)
else:
    st.write("Failed to get the embedding.")
