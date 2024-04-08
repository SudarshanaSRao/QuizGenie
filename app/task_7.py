import streamlit as st
from settings import config

from langchain_core.prompts import PromptTemplate
from langchain_google_vertexai import VertexAI
from langchain_core.runnables import RunnableParallel, RunnablePassthrough

from pdf_processing import DocumentProcessor
from embedding_client import EmbeddingClient
from vector_store import ChromaCollectionCreator


class QuizGenerator:
    def __init__(self, topic=None, num_questions=1, vectorstore=None):
        """
        Initializes the QuizGenerator with a required topic, the number of questions for the quiz,
        and an optional vectorstore for querying related information.

        :param topic: A string representing the required topic of the quiz.
        :param num_questions: An integer representing the number of questions to generate for the quiz, up to a maximum
        of 20.
        :param vectorstore: An optional vectorstore instance (e.g., ChromaDB) to be used for querying information
        related to the quiz topic.
        """
        if not topic:
            self.topic = "General Knowledge"
        else:
            self.topic = topic

        if num_questions > 20:
            raise ValueError("Number of questions cannot exceed 10.")
        self.num_questions = num_questions

        self.vectorstore = vectorstore
        self.llm = None
        self.system_template = """
            You are a subject matter expert on the topic: {topic}
            Follow the instructions to create a quiz question:
            1. Generate a question based on the topic provided and context as key "question"
            2. Provide 4 multiple choice answers to the question as a list of key-value pairs "choices"
            3. Provide the correct answer for the question from the list of answers as key "answer"
            4. Provide an explanation as to why the answer is correct as key "explanation"
            
            You must respond as a JSON object with the following structure:
            {{
                "question": "<question>",
                "choices": [
                    {{"key": "A", "value": "<choice>"}},
                    {{"key": "B", "value": "<choice>"}},
                    {{"key": "C", "value": "<choice>"}},
                    {{"key": "D", "value": "<choice>"}}
                ],
                "answer": "<answer key from choices list>",
                "explanation": "<explanation as to why the answer is correct>"
            }}
            
            Context: {context}
            """

    def init_llm(self):
        """
        Initialize the Large Language Model (LLM) for quiz question generation.
        """
        self.llm = VertexAI(model_name="gemini-pro", temperature=0.4, max_output_tokens=500)

    def generate_question_with_vectorstore(self):
        """
        Generate a quiz question using the topic provided and context from the vectorstore.
        """

        # Initialize the LLM from the 'init_llm' method if not already initialized
        if not self.llm:
            self.init_llm()
            print("LLM initialized")

        # Raise an error if the vectorstore is not initialized on the class
        if not self.vectorstore:
            st.error("Vectorstore is not initialized", icon="🚨")

        # Enable a Retriever using the as_retriever() method on the VectorStore object
        retriever = self.vectorstore.as_retriever()

        # Use the system template to create a PromptTemplate
        prompt_template = PromptTemplate.from_template(self.system_template)

        # RunnableParallel allows Retriever to get relevant documents
        # RunnablePassthrough allows chain.invoke to send self.topic to LLM
        setup_and_retrieval = RunnableParallel({"context": retriever, "topic": RunnablePassthrough()})

        # Create a chain with the Retriever, PromptTemplate, and LLM

        chain = setup_and_retrieval | prompt_template | self.llm

        # Invoke the chain with the topic as input
        response = chain.invoke(self.topic)
        return response


# Test the Object
if __name__ == "__main__":

    embed_config = {
        "model_name": "textembedding-gecko@003",
        "project": config.PROJECT_ID,
        "location": config.PROJECT_LOCATION,
    }

    screen = st.empty()
    with screen.container():
        st.header("Quiz Builder")
        processor = DocumentProcessor()
        processor.ingest_documents()

        embed_client = EmbeddingClient(**embed_config)  # Initialize from Task 4

        chroma_creator = ChromaCollectionCreator(processor, embed_client)

        question = None

        with st.form("Load Data to Chroma"):
            st.subheader("Quiz Builder")
            st.write("Select PDFs for Ingestion, the topic for the quiz, and click Generate!")

            topic_input = st.text_input("Topic for Generative Quiz", placeholder="Enter the topic of the document")
            questions = st.slider("Number of Questions", min_value=1, max_value=10, value=1)

            submitted = st.form_submit_button("Submit")
            if submitted:
                chroma_creator.create_chroma_collection()

                st.write(topic_input)

                # Test the Quiz Generator
                generator = QuizGenerator(topic_input, questions, chroma_creator)
                question = generator.generate_question_with_vectorstore()

    if question:
        screen.empty()
        with st.container():
            st.header("Generated Quiz Question: ")
            st.write(question)
