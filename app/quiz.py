import json

import streamlit as st
from embedding_client import EmbeddingClient
from langchain_core.prompts import PromptTemplate
from langchain_google_vertexai import VertexAI
from pdf_processing import DocumentProcessor
from settings import config
from vector_store import ChromaCollectionCreator


class QuizGenerator:
    def __init__(self, topic=None, num_questions=1, vectorstore=None):
        """
        Initializes the QuizGenerator with a required topic, the number of questions for the quiz,
        and an optional vectorstore for querying related information.

        :param topic: A string representing the required topic of the quiz.
        :param num_questions: An integer representing the number of questions to generate for the quiz, up to a maximum
        of 10.
        :param vectorstore: An optional vectorstore instance (e.g., ChromaDB) to be used for querying information
        related to the quiz topic.
        """
        if not topic:
            self.topic = "General Knowledge"
        else:
            self.topic = topic

        if num_questions > 10:
            raise ValueError("Number of questions cannot exceed 10.")
        self.num_questions = num_questions

        self.vectorstore = vectorstore
        self.llm = None
        self.question_bank = []  # Initialize the question bank to store questions
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
        Initializes and configures the Large Language Model (LLM) for generating quiz questions.

        This method should handle any setup required to interact with the LLM, including authentication,
        setting up any necessary parameters, or selecting a specific model.

        :return: An instance or configuration for the LLM.
        """
        self.llm = VertexAI(
            model_name="gemini-pro",
            temperature=0.8,  # Increased for less deterministic questions
            max_output_tokens=500,
        )

    def generate_question_with_vectorstore(self):
        """
        Generates a quiz question based on the topic provided using a vectorstore

        :return: A JSON object representing the generated quiz question.
        """
        if not self.llm:
            self.init_llm()
        if not self.vectorstore:
            raise ValueError("Vectorstore not provided.")

        from langchain_core.runnables import RunnableParallel, RunnablePassthrough

        # Enable a Retriever
        retriever = self.vectorstore.as_retriever()

        # Use the system template to create a PromptTemplate
        prompt = PromptTemplate.from_template(self.system_template)

        # RunnableParallel allows Retriever to get relevant documents
        # RunnablePassthrough allows chain.invoke to send self.topic to LLM
        setup_and_retrieval = RunnableParallel({"context": retriever, "topic": RunnablePassthrough()})
        # Create a chain with the Retriever, PromptTemplate, and LLM
        chain = setup_and_retrieval | prompt | self.llm

        # Invoke the chain with the topic as input
        response = chain.invoke(self.topic)
        return response

    def generate_quiz(self) -> list:
        """
        This method orchestrates the quiz generation process by utilizing the `generate_question_with_vectorstore`
        method to generate each question and the `validate_question` method to ensure its uniqueness before adding it
        to the quiz.

        Returns:
        - A list of dictionaries, where each dictionary represents a unique quiz question generated based on the topic.

        Note: This method relies on `generate_question_with_vectorstore` for question generation and `validate_question`
        for ensuring question uniqueness. Ensure `question_bank` is properly initialized and managed.
        """
        self.question_bank = []  # Reset the question bank
        retry_limit = 3  # Maximum number of retries to generate a unique question

        for _ in range(self.num_questions):
            question_str = self.generate_question_with_vectorstore()
            retries = 0

            try:
                # Convert the JSON String to a dictionary
                question = json.loads(question_str)
                print("Converted the JSON String to a dictionary")
            except json.JSONDecodeError:
                print("Failed to decode question JSON.")
                continue  # Skip this iteration if JSON decoding fails

            # Validate the question using the validate_question method
            if self.validate_question(question):
                print("Successfully generated unique question")
                # Add the valid and unique question to the bank
                self.question_bank.append(question)
            else:
                print("Duplicate or invalid question detected.")
                # Retry generating a new question up to the retry limit
                while retries < retry_limit:
                    question = json.loads(self.generate_question_with_vectorstore())
                    retries += 1

                    if self.validate_question(question):
                        self.question_bank.append(question)
                        break

                    retries += 1

                if retries > retry_limit:
                    print("Failed to generate a unique question after multiple attempts.")
                    self.generate_quiz()

        return self.question_bank

    def validate_question(self, question: dict) -> bool:
        """
        This method checks if the provided question (as a dictionary) is unique based on its text content compared to
        previously generated questions stored in `question_bank`. The goal is to ensure that no duplicate questions
        are added to the quiz.

        Parameters:
        - question: A dictionary representing the generated quiz question, expected to contain at least a "question"
        key.

        Returns:
        - A boolean value: True if the question is unique, False otherwise.

        Note: This method assumes `question` is a valid dictionary and `question_bank` has been properly initialized.
        """
        # Consider missing 'question' key as invalid in the dict object
        if "question" not in question:
            is_unique = False

        # Check if a question with the same text already exists in the self.question_bank
        question_text = question["question"]
        for existing_question in self.question_bank:
            if existing_question["question"] == question_text:
                is_unique = False
                break

        is_unique = True
        return is_unique


class QuizManager:

    def __init__(self, questions: list):
        """
        This task involves setting up the `QuizManager` class by initializing it with a list of quiz question objects.
        Each quiz question object is a dictionary that includes the question text, multiple choice options, the correct
        answer, and an explanation. The initialization process should prepare the class for managing these quiz
        questions, including tracking the total number of questions.

        Parameters:
        - questions: A list of dictionaries, where each dictionary represents a quiz question along with its choices,
        correct answer, and an explanation.

        Note: This initialization method is crucial for setting the foundation of the `QuizManager` class, enabling it
        to manage the quiz questions effectively. The class will rely on this setup to perform operations such as
        retrieving specific questions by index and navigating through the quiz.
        """
        self.questions = questions
        self.total_questions = len(questions)

    def get_question_at_index(self, index: int):
        """
        Retrieves the quiz question object at the specified index. If the index is out of bounds,
        it restarts from the beginning index.

        :param index: The index of the question to retrieve.
        :return: The quiz question object at the specified index, with indexing wrapping around if out of bounds.
        """
        # Ensure index is always within bounds using modulo arithmetic
        valid_index = index % self.total_questions
        return self.questions[valid_index]

    def next_question_index(self, direction=1):
        """
        Develop a method to navigate to the next or previous quiz question by adjusting the `question_index` in
        Streamlit's session state. This method should account for wrapping, meaning if advancing past the last
        question or moving before the first question, it should continue from the opposite end.

        Parameters:
        - direction: An integer indicating the direction to move in the quiz questions list (1 for next, -1 for
        previous).

        Note: Ensure that `st.session_state["question_index"]` is initialized before calling this method. This
        navigation method enhances the user experience by providing fluid access to quiz questions.
        """
        current_index = st.session_state["question_index"]
        new_index = (current_index + direction) % (self.total_questions)
        st.session_state["question_index"] = new_index


# Test Generating the Quiz
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

        embed_client = EmbeddingClient(**embed_config)

        chroma_creator = ChromaCollectionCreator(processor, embed_client)

        question = None
        question_bank = None

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
                question_bank = generator.generate_quiz()

    if question_bank:
        screen.empty()
        with st.container():
            st.header("Generated Quiz Question: ")
            quiz_manager = QuizManager(question_bank)
            # Format the question and display
            with st.form("Multiple Choice Question"):
                index_question = quiz_manager.get_question_at_index(0)
                # Unpack choices for radio
                choices = []
                for choice in index_question["choices"]:  # For loop unpack the data structure
                    key = choice["key"]
                    value = choice["value"]
                    choices.append(f"{key}) {value}")

                st.markdown(index_question["question"])  # Display the question
                answer = st.radio("Choose the correct answer", choices)  # Display the radio button with the choices
                st.form_submit_button("Submit")

                if submitted:  # On click submit
                    correct_answer_key = index_question["answer"]
                    if answer.startswith(correct_answer_key):  # Check if answer is correct
                        st.success("Correct!")
                    else:
                        st.error("Incorrect!")
