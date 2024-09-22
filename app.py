import chainlit as cl
import openai
import os
from langsmith.wrappers import wrap_openai
from langsmith import traceable
from prompts import INITIAL_SYSTEM_PROMPT
from pydantic import BaseModel
from search_handler import search, Provider
from llama_index.readers.web import BeautifulSoupWebReader
from llama_index.core import VectorStoreIndex

API_KEY = os.getenv("OPENAI_API_KEY")
ENDPOINT_URL = os.getenv("OPENAI_ENDPOINT")
MODEL = "gpt-4o-2024-08-06"

client = wrap_openai(openai.AsyncClient(api_key=API_KEY, base_url=ENDPOINT_URL))


class RecommendationResponse(BaseModel):
    is_recommendation_query: bool
    product_type: str
    max_price: int
    features: str


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
    response_msg = cl.Message(content="")
    await response_msg.send()

    if recommendation_response.is_recommendation_query:
        if not recommendation_response.max_price:
            response_msg.content = "What is the price range you are looking for ?"
        elif len(recommendation_response.features)==0:
            response_msg.content = "What are the features expected in the "+ recommendation_response.product_type + "?"
        else:
            await cl.Message(content="Processing your request...").send()
            search_string = ("Top " + recommendation_response.product_type
                             + " with price range of " + str(recommendation_response.max_price)
                             + " with features " + recommendation_response.features)
            print("Searching for " + search_string)
            results = search(search_query=search_string, provider=Provider.DuckDuckGo)  #provider=Provider.Google
            # load search result pages
            documents = BeautifulSoupWebReader().load_data(urls=results)

            # Create an index from the documents
            index = VectorStoreIndex.from_documents(documents)

            # Create a query engine
            query_engine = index.as_query_engine()
            response_msg.content = query_engine.query(search_string)
            print(response_msg.content)
        # response_msg.content = f"I recommend you buy the most expensive {recommendation_response.product_type} out there!"
    else:
        response_msg.content = "Please suggest a type of product you would like to buy."
    # await response_msg.update()

    message_history.append({"role": "assistant", "content": response_msg.content})
    print(message_history)
    cl.user_session.set("message_history", message_history)
    await cl.Message(content=response_msg.content).send()

if __name__ == "__main__":
    from chainlit.cli import run_chainlit
    run_chainlit(__file__)



