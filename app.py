import chainlit as cl
import openai
import os
from llama_index.core import SummaryIndex
from llama_index.readers.web import SimpleWebPageReader


API_KEY = os.getenv("OPENAI_API_KEY")
ENDPOINT_URL = os.getenv("OPENAI_ENDPOINT")
MODEL = "gpt-4"

client = openai.AsyncClient(api_key=API_KEY, base_url=ENDPOINT_URL)


@cl.on_message
async def handle_message(message):
    query = message.content
    response = await client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": "Determine if the user is asking for a product recommendation. Respond with 'YES' or 'NO' only.",
            },
            {"role": "user", "content": query},
        ],
    )
    is_recommendation_query = (
        response.choices[0].message.content.strip().upper() == "YES"
    )
    print(f"is_recommendation_query: {is_recommendation_query}")

    if is_recommendation_query:
        response_text = "I recommend you buy a iPhone 16 Pro."
    else:
        response_text = "Please suggest a type of product you would like to buy."

    await cl.Message(
        content=response_text,
    ).send()
