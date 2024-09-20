import chainlit as cl
import openai
import os
from pydantic import BaseModel
from langsmith.wrappers import wrap_openai
from langsmith import traceable

API_KEY = os.getenv("OPENAI_API_KEY")
ENDPOINT_URL = os.getenv("OPENAI_ENDPOINT")
MODEL = "gpt-4o-2024-08-06"

client = wrap_openai(openai.AsyncClient(api_key=API_KEY, base_url=ENDPOINT_URL))


class RecommendationResponse(BaseModel):
    is_recommendation_query: bool
    product_type: str


@traceable
@cl.on_message
async def handle_message(message):
    query = message.content
    response = await client.beta.chat.completions.parse(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": "Determine if the user is asking for a product recommendation. Respond with a JSON object containing 'is_recommendation_query' (boolean) and 'product_type' (string).",
            },
            {"role": "user", "content": query},
        ],
        response_format=RecommendationResponse,
    )
    recommendation_response = response.choices[0].message.parsed
    print(f"is_recommendation_query: {recommendation_response.is_recommendation_query}")
    print(f"product_type: {recommendation_response.product_type}")

    if recommendation_response.is_recommendation_query:
        response_text = f"I recommend you buy the most expensive {recommendation_response.product_type} out there!"
    else:
        response_text = "Please suggest a type of product you would like to buy."

    await cl.Message(content=response_text).send()
