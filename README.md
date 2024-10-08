# Consumer Researcher AI Chat App

## Project Overview

This project is the capstone for the Max Academy AI Bootcamp. It's an AI-powered chat application designed to assist users with consumer research. The app reviews web content and provides personalized product recommendations based on user interactions.

## Features

- AI-driven chat interface for user queries
- Web content analysis for product research
- Personalized product recommendations
- User-friendly interface

## Setup Instructions

Follow these steps to set up the project on your local machine:

1. Clone the repository:
   ```
   git clone https://github.com/Codepath-AI-Team-NikSan/capstone.git
   cd capstone
   ```

2. Create a virtual environment:
   ```
   python3 -m venv venv
   source .venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Create a `.env` file in the project root:
   - Copy the `.env.sample` file and rename it to `.env`
   - Fill in the required variables as specified in the `.env.sample` file

   For example, your `.env` file might look like this:
   ```
   OPENAIAPI_KEY=YOUR_KEY_HERE
   OPENAI_ENDPOINT=https://api.openai.com/v1
   # Add any other variables specified in .env.sample
   ```

5. Run the application:
   ```
   chainlit run app.py -w
   ```
   The app will be accessible at `http://localhost:8000`


## Usage

After setting up the project, users can interact with the AI chat interface to ask questions about products, request recommendations, or seek consumer advice. The AI will analyze web content and provide relevant information and suggestions based on the user's queries.


## Week 2 Capstone Milestones
- [x] ~~Create a public GitHub repo with a README.md that describes the project (@nikrad)~~
- [x] ~~Create the app scaffold (@nikrad)~~
  - [x] ~~Basic Python project with a .env (@nikrad)~~
  - [x] ~~Tracing with LangSmith or Langfuse (@nikrad)~~
  - [x] ~~Chainlit wired to OpenAI with chat history (@nikrad)~~
- [x] ~~Design the main prompt(s) (@sanal @nikrad)~~
- [x] ~~Create an evaluation dataset (10 examples) (@nikrad)~~
- [x] ~~(stretch) Set up LlamaIndex loaders (e.g., email, Slack, wherever your data is coming from) (@sanal)~~
- [x] ~~(stretch) Set up your RAG pipeline (@sanal)~~
- [x] ~~(stretch) Run an LLM-as-a-judge evaluation test (@nikrad)~~

## Week 3 Capstone Milestones
- [x] ~~Implement a RAG pipeline (@sanal)~~
- [x] ~~Implement at least one function call (@nikrad)~~
- [x] ~~(stretch) Run an LLM-as-a-judge evaluation test (@sanal)~~

## Week 4 Capstone Milestones
- [x] ~~Include links to buy recommended products (@nikrad)~~

