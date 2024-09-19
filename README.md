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
   git clone https://github.com/your-username/consumer-research-ai-chat.git
   cd consumer-research-ai-chat
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

## Usage

After setting up the project, users can interact with the AI chat interface to ask questions about products, request recommendations, or seek consumer advice. The AI will analyze web content and provide relevant information and suggestions based on the user's queries.
