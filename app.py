import chainlit as cl
import openai
import os
from langsmith.wrappers import wrap_openai
from langsmith import traceable
from prompts import INITIAL_SYSTEM_PROMPT
from pydantic import BaseModel


API_KEY = os.getenv("OPENAI_API_KEY")
ENDPOINT_URL = os.getenv("OPENAI_ENDPOINT")
MODEL = "gpt-4o-2024-08-06"

client = wrap_openai(openai.AsyncClient(api_key=API_KEY, base_url=ENDPOINT_URL))


class RecommendationResponse(BaseModel):
    is_recommendation_query: bool
    product_type: str
    max_price: int


@traceable
@cl.on_message
async def handle_message(message):
    # Maintain an array of messages in the user session
    message_history = cl.user_session.get("message_history", [])
    query = message.content
    if not len(message_history) or message_history[0].get("role") != "system":
        message_history.append({"role": "system", "content": INITIAL_SYSTEM_PROMPT})
    message_history.append({"role": "user", "content": query})
    response = await client.beta.chat.completions.parse(
        model=MODEL,
        messages=message_history,
        response_format=RecommendationResponse,
    )
    message_history.append(
        {"role": "assistant", "content": response.choices[0].message.content}
    )
    recommendation_response = response.choices[0].message.parsed
    print(f"is_recommendation_query: {recommendation_response.is_recommendation_query}")
    print(f"product_type: {recommendation_response.product_type}")
    if recommendation_response.is_recommendation_query:
        response_text = f"I recommend you buy the most expensive {recommendation_response.product_type} out there!"
    else:
        response_text = "Please suggest a type of product you would like to buy."

    message_history.append({"role": "assistant", "content": response_text})
    print(message_history)
    cl.user_session.set("message_history", message_history)
    await cl.Message(content=response_text).send()
