import streamlit as st
from embedding_client import EmbeddingClient
from pdf_processing import DocumentProcessor
from quiz import QuizGenerator, QuizManager
from settings import config
from vector_store import ChromaCollectionCreator

if __name__ == "__main__":
    embed_config = {
        "model_name": "textembedding-gecko@003",
        "project": config.PROJECT_ID,
        "location": config.PROJECT_LOCATION,
    }

    # Add Session State
    if "question_bank" not in st.session_state or len(st.session_state["question_bank"]) == 0:
        screen = st.empty()
        with screen.container():
            st.header("Quiz Builder")

            # Create a new st.form flow control for Data Ingestion
            with st.form("Load Data to Chroma"):
                st.write("Select PDFs for Ingestion, the topic for the quiz, and click Generate!")

                processor = DocumentProcessor()
                processor.ingest_documents()

                embed_client = EmbeddingClient(**embed_config)

                chroma_creator = ChromaCollectionCreator(processor, embed_client)

                topic_input = st.text_input("Topic for Generative Quiz", placeholder="Enter the topic of the document")
                questions = st.slider("Number of Questions", min_value=1, max_value=10, value=1)

                submitted = st.form_submit_button("Submit")

                if submitted:
                    chroma_creator.create_chroma_collection()

                    if len(processor.pages) > 0:

                        st.write(f"Generating {questions} questions for topic: {topic_input}")

                    # Initialize a QuizGenerator class using the topic, number of questrions, and the chroma collection
                    with st.spinner("Generating Quiz..."):
                        generator = QuizGenerator(topic_input, questions, chroma_creator)
                        question_bank = generator.generate_quiz()

                        st.session_state["question_bank"] = question_bank
                        st.session_state["display_quiz"] = True
                        st.session_state["question_index"] = 0
                        st.session_state["score"] = 0
                        st.session_state["last_question"] = False

                    st.form_submit_button("Start Quiz")

    elif st.session_state["display_quiz"]:

        st.empty()
        with st.container():
            st.header("Question: " + str(st.session_state["question_index"] + 1))
            quiz_manager = QuizManager(st.session_state["question_bank"])

            # Format the question and display it
            with st.form("MCQ"):

                index_question = quiz_manager.get_question_at_index(st.session_state["question_index"])

                # Unpack choices for radio button
                choices = []
                for choice in index_question["choices"]:
                    key = choice["key"]
                    value = choice["value"]
                    choices.append(f"{key}) {value}")

                # Display the Question
                st.write(f"{st.session_state['question_index'] + 1}. {index_question['question']}")
                answer = st.radio("Choose an answer", choices, index=None)

                answer_choice = st.form_submit_button("Submit")

                if answer_choice and answer is not None:
                    correct_answer_key = index_question["answer"]
                    if answer.startswith(correct_answer_key):
                        st.success("Correct!")
                        st.session_state["score"] += 1
                    else:
                        st.error("Incorrect!")
                        st.info(f"Explanation: {index_question['explanation']}")

                if st.session_state["question_index"] == 0:
                    st.form_submit_button(
                        "Next Question", on_click=lambda: quiz_manager.next_question_index(direction=1)
                    )

                elif st.session_state["question_index"] < len(st.session_state["question_bank"]) - 1:
                    col1, col2, col3, col4 = st.columns(4)

                    with col1:
                        st.form_submit_button(
                            "Previuos Question", on_click=lambda: quiz_manager.next_question_index(direction=-1)
                        )
                    with col4:
                        st.form_submit_button(
                            "Next Question", on_click=lambda: quiz_manager.next_question_index(direction=1)
                        )

                else:
                    st.form_submit_button(
                        "Previuos Question", on_click=lambda: quiz_manager.next_question_index(direction=-1)
                    )
                    st.form_submit_button(
                        "Finish Quiz",
                        on_click=lambda: st.session_state.update({"display_quiz": False, "last_question": True}),
                    )

    elif st.session_state["last_question"]:
        st.empty()
        with st.container():
            st.header("End of Quiz")
            with st.form("End"):
                st.subheader(
                    f"You answered {st.session_state['score']} out of {len(st.session_state['question_bank'])} correct"
                    "answered correctly."
                )
                st.form_submit_button(
                    "End Quiz",
                    on_click=lambda: st.session_state.update({"display_quiz": False, "question_bank": []}),
                )
                restart = st.form_submit_button(
                    "Restart Quiz",
                    on_click=lambda: st.session_state.update({"display_quiz": True, "question_index": 0, "score": 0}),
                )
