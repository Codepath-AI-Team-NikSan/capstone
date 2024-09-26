import chainlit as cl
import openai
import os
from langsmith.wrappers import wrap_openai
from langsmith import traceable
from prompts import INITIAL_SYSTEM_PROMPT, SEARCH_RESULT_PROMPT
from pydantic import BaseModel
from search_handler import search, Provider
from llama_index.readers.web import BeautifulSoupWebReader
from llama_index.core import VectorStoreIndex
from CustomWebReader import CustomWebReader

API_KEY = os.getenv("OPENAI_API_KEY")
ENDPOINT_URL = os.getenv("OPENAI_ENDPOINT")
MODEL = "gpt-4o-2024-08-06"

client = wrap_openai(openai.AsyncClient(api_key=API_KEY, base_url=ENDPOINT_URL))


class RecommendationResponse(BaseModel):
    is_recommendation_query: bool
    product_type: str
    max_price: int
    features: str


@cl.on_chat_start
async def handle_chat_start():
    message_history = [{"role": "system", "content": INITIAL_SYSTEM_PROMPT}]
    cl.user_session.set("message_history", message_history)


@traceable
@cl.on_message
async def handle_message(message):
    # Maintain an array of messages in the user session
    message_history = cl.user_session.get("message_history", [])
    query = message.content

    # Add the user's message to the message history
    message_history.append({"role": "user", "content": query})
    # Send the message history to the OpenAI API
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
    if recommendation_response.is_recommendation_query:
        if not recommendation_response.product_type:
            msg = "What type of product are you looking for?"
            response_msg = cl.Message(content=msg)
            await response_msg.send()
        elif not recommendation_response.max_price:
            msg = f"What price range or maximum price do you have mind for the {recommendation_response.product_type}?"
            response_msg = cl.Message(content=msg)
            await response_msg.send()
        elif len(recommendation_response.features) == 0:
            msg = f"Are there any specific features or characteristics you're looking for in the {recommendation_response.product_type}?"
            response_msg = cl.Message(content=msg)
            await response_msg.send()
        else:
            response_msg = cl.Message(content="Processing your request...")
            await response_msg.send()
            search_string = (
                f"Top {recommendation_response.product_type} with price range of "
                f"{recommendation_response.max_price} with features "
                f"{recommendation_response.features}"
            )
            response_msg.content = f"Searching for `{search_string}`..."
            await response_msg.update()

            search_prompt = SEARCH_RESULT_PROMPT.format(
                recommendation_response.product_type,
                recommendation_response.max_price,
                recommendation_response.features,
            )
            print(f"search_prompt: {search_prompt}")
            search_result = search_and_process(search_string, search_prompt)
            print(f"search_result: {search_result}")

            response_msg.content = str(search_result)
            await response_msg.update()
    else:
        response_msg.content = "Please suggest a type of product you would like to buy."
        await response_msg.send()

    message_history.append({"role": "assistant", "content": response_msg.content})
    print(f"message_history: {message_history}")
    cl.user_session.set("message_history", message_history)


@traceable
def search_and_process(search_string, search_prompt):
    results = search(
        search_query=search_string, provider=Provider.DuckDuckGo, max_results=10
    )  # provider=Provider.Google
    print(f"results: {results}")

    # Load search result pages
    try:
        # documents = BeautifulSoupWebReader().load_data(urls=results)  #BSReader intermittently getting stuck
        documents = CustomWebReader().load_data(urls=results)
    except Exception as e:
        print(f"Error loading data from URLs: {e}")
        documents = []
    print(f"Created {len(documents)} documents")

    # Create an index from the documents
    index = VectorStoreIndex.from_documents(documents)
    print(f"Created VectorStoreIndex")

    # Create a query engine
    query_engine = index.as_query_engine()
    return query_engine.query(search_prompt)


if __name__ == "__main__":
    from chainlit.cli import run_chainlit

    run_chainlit(__file__)
