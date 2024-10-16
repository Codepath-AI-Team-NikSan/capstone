import json
import os

import chainlit as cl
import openai

from datetime import datetime
from dotenv import load_dotenv
from langsmith import traceable
from langsmith.wrappers import wrap_openai
from llama_index.core import Document, VectorStoreIndex

from async_web_reader import AsyncWebReader
from helpers import dprint
from prompts import FN_CALL_SYSTEM_PROMPT, FN_CALL_RAG_PROMPT, PURCHASING_LINKS_PROMPT
from search_handler import search, Provider
from tool_calls import (
    PRODUCT_SEARCH_TOOL,
    ADD_TO_WISH_LIST_TOOL,
    GET_WISH_LIST_TOOL,
    REMOVE_FROM_WISH_LIST_TOOL,
    ADD_TO_ORDER_TOOL,
    GET_ORDERS_TOOL,
)
from wishlist import add_to_wishlist, get_wishlist, remove_from_wishlist
from orders import add_to_orders, get_orders

load_dotenv()

API_KEY = os.getenv("OPENAI_API_KEY")
ENDPOINT_URL = os.getenv("OPENAI_ENDPOINT")
MODEL = "gpt-4o"
GEN_KWARGS = {"model": MODEL, "temperature": 0.3, "max_tokens": 500}

client = wrap_openai(openai.AsyncClient(api_key=API_KEY, base_url=ENDPOINT_URL))

WELCOME_MSG = """\
Hi! 👋 I'm here to help you find the best products out there. \
Whether you're shopping for tech, home goods, or anything in between, I'm ready to offer recommendations backed by \
expert research and real-world testing. 🛒✨

Let's get started! What type of product are you looking for?
"""


@traceable
async def generate_response(client, message_history, gen_kwargs):
    """
    Construct the streaming LLM response, including function calls. Updates the UI with the response as it's generated.

    Args:
        client: The OpenAI client used for generating the response.
        message_history (list): A list of previous messages in the conversation.
        gen_kwargs (dict): A dictionary containing generation parameters.

    Returns:
        The generated response from the AI model.
    """
    ui_response_message = None

    stream = await client.chat.completions.create(
        messages=message_history,
        stream=True,
        tools=[
            PRODUCT_SEARCH_TOOL,
            ADD_TO_WISH_LIST_TOOL,
            GET_WISH_LIST_TOOL,
            REMOVE_FROM_WISH_LIST_TOOL,
            ADD_TO_ORDER_TOOL,
            GET_ORDERS_TOOL,
        ],
        **gen_kwargs,
    )
    response = {}
    async for part in stream:
        new_delta = part.choices[0].delta
        if new_delta.role is not None:
            response["role"] = new_delta.role
        if (
            new_delta.tool_calls is not None
            and len(new_delta.tool_calls) > 0
            and new_delta.tool_calls[0].function is not None
        ):
            fn_call = new_delta.tool_calls[0].function
            if fn_call.name:
                response["func_call"] = {"name": fn_call.name}
            if fn_call.arguments:
                if "arguments" not in response["func_call"]:
                    response["func_call"]["arguments"] = ""
                response["func_call"]["arguments"] += fn_call.arguments
        else:
            new_content = new_delta.content or ""
            if "content" not in response:
                response["content"] = ""
            response["content"] += new_content
            if len(new_content):
                if ui_response_message is None:
                    ui_response_message = cl.Message(content="")
                    await ui_response_message.send()
                await ui_response_message.stream_token(new_content)

    if ui_response_message is not None:
        await ui_response_message.update()

    return response


def get_sources_list(source_urls):
    """
    Formats the sources from the given RAG results.
    """
    citations = [f"• {url}" for url in source_urls]
    sources_list = "\n".join(citations)
    return sources_list


def get_product_links_list(webpages, source_urls, recommendation_blurb):
    """
    Extracts and formats the purchasing links from the given product recommendation blurb.
    """
    product_links_list = ""
    docs = [
        Document(text=page["html"]) for page in webpages if page["url"] in source_urls
    ]
    if not len(docs):
        return product_links_list

    index = VectorStoreIndex.from_documents(docs)
    query_engine = index.as_query_engine()
    prompt = PURCHASING_LINKS_PROMPT.format(recommendation_blurb=recommendation_blurb)
    product_links_rag_response = str(query_engine.query(prompt).response)
    dprint(f"product_links_rag_response: {product_links_rag_response}")
    if not product_links_rag_response:
        return product_links_list

    product_links_result = json.loads(product_links_rag_response)
    return "\n".join(
        [
            f"• {product_name}: {link}\n"
            for (product_name, link) in json.loads(product_links_rag_response)
            if len(link)
        ]
    )


@traceable
async def search_and_process(search_query, llm_prompt, ui_status_message):
    """
    Performs a web search based on the given query, processes the search results,
    and generates a response using RAG.

    Args:
        search_query (str): The search query to be used for web search.
        llm_prompt (str): The prompt to be used for the language model.
        ui_status_message (object): An object used to update the UI with status messages.

    Returns:
        None: This function updates the UI status message with the final RAG response.
    """
    ui_status_message.content = f'🔍 Searching the web for `"{search_query}"`...'
    await ui_status_message.update()

    search_results = search(search_query=search_query, max_results=15)
    ui_status_message.content = f"👀 Reviewing {len(search_results)} results closely for the best recommendations..."
    await ui_status_message.update()

    # Load search result pages
    try:
        reader = AsyncWebReader()
        webpages = await reader.load_data(urls=search_results)
    except Exception as e:
        dprint(f"Error loading data from URLs: {e}")
        webpages = []

    # Generate product recommendations
    docs = [
        Document(text=page["text"], metadata={"url": page["url"]}) for page in webpages
    ]
    index = VectorStoreIndex.from_documents(docs)
    query_engine = index.as_query_engine()
    rag_prompt = FN_CALL_RAG_PROMPT.format(llm_prompt=llm_prompt)
    dprint(f"rag_prompt: {rag_prompt}")
    rag_results = query_engine.query(rag_prompt)
    rag_response = str(rag_results.response)
    dprint(f"rag_response: {rag_response}")
    dprint(f"rag_results.metadata: {rag_results.metadata}")

    # Add sources for product recommendations
    ui_status_message.content = "📚 Citing my sources to give credit where it's due..."
    await ui_status_message.update()
    source_urls = {
        rag_results.metadata[source]["url"]
        for source in rag_results.metadata
        if rag_results.metadata[source]["url"]
    }
    sources_list = get_sources_list(source_urls)

    # Find purchasing links for product recommendations
    ui_status_message.content = "🎣 Fetching link(s) to buy product(s)..."
    await ui_status_message.update()
    product_links_list = get_product_links_list(webpages, source_urls, rag_response)

    recommendation_response = (
        f"{rag_response}\n\n\n**🔗 Review Source(s):**\n{sources_list}"
    )
    if len(product_links_list):
        recommendation_response += f"\n\n\n**🛍️ Link(s) to Buy:**\n{product_links_list}"

    ui_status_message.content = recommendation_response
    await ui_status_message.update()

    return recommendation_response


@traceable
@cl.on_chat_start
async def handle_chat_start():
    # Include the actually current date in the system prompt for the LLM for times when
    # it decides to add the current year to the search query
    await cl.Message(content=WELCOME_MSG).send()
    today = datetime.today()
    current_date = today.strftime("%A, %B %d, %Y")
    system_prompt = FN_CALL_SYSTEM_PROMPT.format(current_date=current_date)
    message_history = [{"role": "system", "content": system_prompt}]
    cl.user_session.set("message_history", message_history)


@traceable
@cl.on_message
async def handle_message(message):
    # Maintain an array of messages in the user session
    message_history = cl.user_session.get("message_history", [])
    query = message.content
    # Add the user's message to the message history
    message_history.append({"role": "user", "content": query})

    response = await generate_response(client, message_history, GEN_KWARGS)
    dprint(f"LLM Response: {response}")

    if response.get("func_call") and response["func_call"]["name"] == "product_search":
        arguments = json.loads(response["func_call"]["arguments"])
        search_query = arguments["google_search_query"]
        llm_prompt = arguments["llm_prompt"]
        message_history.append(
            {
                "role": "assistant",
                "content": f'Calling product_search("{search_query}", "{llm_prompt}")',
            }
        )

        status_message = await cl.Message(content="").send()
        search_response = await search_and_process(
            search_query, llm_prompt, status_message
        )
        # Update the message history with the RAG response
        message_history.append({"role": "assistant", "content": search_response})
    elif (
        response.get("func_call") and response["func_call"]["name"] == "add_to_wishlist"
    ):
        arguments = json.loads(response["func_call"]["arguments"])
        name = arguments["name"]
        price = arguments["price"]
        description = arguments["description"]
        sources = arguments["sources"]
        buy_links = arguments["buy_links"] if "buy_links" in arguments else None
        message_history.append(
            {
                "role": "assistant",
                "content": f'Calling add_to_wishlist("{name}", "{price}","{description}", "{sources}", "{buy_links}")',
            }
        )
        response = add_to_wishlist(name, price, description, sources, buy_links)
        await cl.Message(content=response).send()
        message_history.append(
            {
                "role": "assistant",
                "content": "wishlist :" + get_wishlist(wishlist_str=True),
            }
        )
    elif response.get("func_call") and response["func_call"]["name"] == "get_wishlist":
        message_history.append(
            {
                "role": "assistant",
                "content": f"Calling get_wishlist()",
            }
        )
        response = get_wishlist(wishlist_str=True)
        await cl.Message(content=response).send()
    elif (
        response.get("func_call")
        and response["func_call"]["name"] == "remove_from_wishlist"
    ):
        arguments = json.loads(response["func_call"]["arguments"])
        name = arguments["name"]
        message_history.append(
            {
                "role": "assistant",
                "content": f'Calling remove_from_wishlist("{name}")',
            }
        )
        response = remove_from_wishlist(name)
        await cl.Message(content=response).send()
        wishlist = get_wishlist(wishlist_str=True)
        if wishlist is not None:
            message_history.append(
                {
                    "role": "assistant",
                    "content": "wishlist :" + get_wishlist(wishlist_str=True),
                }
            )
    elif response.get("func_call") and response["func_call"]["name"] == "add_to_orders":
        arguments = json.loads(response["func_call"]["arguments"])
        name = arguments["name"]
        price = arguments["price"]
        description = arguments["description"]
        quantity = arguments["quantity"]
        message_history.append(
            {
                "role": "assistant",
                "content": f'Calling add_to_orders("{name}", "{price}","{description}", "{quantity}")',
            }
        )
        response = add_to_orders(name, price, description, quantity)
        await cl.Message(content=response).send()
        message_history.append(
            {"role": "assistant", "content": "wishlist :" + get_orders(orders_str=True)}
        )
    elif response.get("func_call") and response["func_call"]["name"] == "get_orders":
        message_history.append(
            {
                "role": "assistant",
                "content": f"Calling get_orders()",
            }
        )
        response = get_orders(orders_str=True)
        await cl.Message(content=response).send()
    elif response.get("content"):
        message_history.append({"role": "assistant", "content": response["content"]})

    dprint(f"message_history: {message_history}")
    cl.user_session.set("message_history", message_history)


if __name__ == "__main__":
    from chainlit.cli import run_chainlit

    run_chainlit(__file__)
