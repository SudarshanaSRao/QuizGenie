# Gemini Quizify

## Overview

Gemini Quizify is an AI-powered quiz platform crafted to offer students and learners an interactive way to solidify their grasp of different subjects. Using advanced AI, the tool generates quizzes from documents users provide, giving immediate feedback and thorough explanations to aid in better understanding and memory retention, thereby enriching the learning process.

## Mission Objective:

The lack of accessible and effective means for students and learners to reinforce their understanding of various topics. Recognizing the challenge of obtaining timely feedback and engaging in unlimited practice, the team is developing an AI-generated assessment and quiz tool. This tool aims to provide users with instant feedback and comprehensive explanations, thus facilitating deeper comprehension and retention of knowledge. By dynamically generating quizzes based on user-provided documents, ranging from textbooks to scholarly papers, the tool offers a tailored learning experience. The end result will be a user-friendly platform that empowers individuals to hone their skills, solidify their understanding, and ultimately excel in their academic pursuits.

## Features:

- **AI-Generated Assessments and Quizzes:** Utilizing artificial intelligence, the tool will dynamically generate quizzes and assessments based on user-provided documents, such as textbooks and scholarly papers.
- **Instant Feedback:** Users will receive immediate feedback on their quiz performance, allowing them to quickly identify areas of strength and areas needing improvement.
- **Comprehensive Explanations:** Detailed explanations will be provided for each question, enabling users to understand the reasoning behind correct answers and learn from mistakes.
- **Tailored Learning Experience:** The quizzes will be customized to the content of the user-provided documents, ensuring relevance and alignment with the topics being studied.

## Technologies Used

- **Python** serves as the foundational language for crafting Gemini Quizify's backend logic.
- **Langchain** is harnessed for proficient natural language processing, empowering the tool to adeptly understand and dissect textual content.
- **Chromadb** stands as the robust database management system, ensuring swift storage and retrieval of user data and quiz content.
- **Google** Gemini plays a pivotal role in AI-driven content analysis and generation, enabling the tool to dynamically craft quizzes from user-supplied documents.
- **Streamlit** enriches the user experience by facilitating the creation of interactive web applications with Python, enhancing the accessibility and usability of Gemini Quizify.

## Tasks Completed

The project files encompass the following tasks:

1. Integration of Google Service Account for authentication.
2. Implementing a PDF loader for document ingestion.
3. Processing documents using Google Gemini.
4. Generating text embeddings using Langchain.
5. Building a user interface with Streamlit.
6. Creating quizzes based on user-specified topics.
7. Supplying explanations for quiz answers.
8. Handling errors and performing validation.

## Implementation Flow

![Task 9 Overview](https://github.com/Rohit04121998/Gemini-Quizify/blob/main/assets/implementation.png)

### Work Flow

**PDF Input**

![Generate Quiz Algorithm Input](https://github.com/Rohit04121998/Gemini-Quizify/blob/main/assets/pdf_input.png)


**Generated Questions**

![Screen State Handling](https://github.com/Rohit04121998/Gemini-Quizify/blob/main/assets/generated_question.png)

## Issues Faced

### ⚠️ Question Quality

The current iteration of Gemini-pro predominantly produces JSON markdown results, which occasionally leads to suboptimal question generation. As a remedy, a straightforward prompt engineering methodology has been experimented with and found effective. It has been observed that implementing this prompt engineering approach can significantly enhance the success rate to approximately 80%.
