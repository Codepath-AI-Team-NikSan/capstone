import json
import os

import chainlit as cl
import openai

from dotenv import load_dotenv
from langsmith import traceable
from langsmith.wrappers import wrap_openai
from llama_index.core import VectorStoreIndex

from CustomWebReader import CustomWebReader
from helpers import dprint
from prompts import FN_CALL_SYSTEM_PROMPT, FN_CALL_RAG_PROMPT
from search_handler import search, Provider
from tool_calls import PRODUCT_SEARCH_TOOL

load_dotenv()

API_KEY = os.getenv("OPENAI_API_KEY")
ENDPOINT_URL = os.getenv("OPENAI_ENDPOINT")
MODEL = "gpt-4o"
GEN_KWARGS = {"model": MODEL, "temperature": 0.3, "max_tokens": 500}

client = wrap_openai(openai.AsyncClient(api_key=API_KEY, base_url=ENDPOINT_URL))


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
        messages=message_history, stream=True, tools=[PRODUCT_SEARCH_TOOL], **gen_kwargs
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
    ui_status_message.content = f'Searching the web for `"{search_query}"`...'
    await ui_status_message.update()

    search_results = search(
        search_query=search_query, provider=Provider.Google, max_results=20
    )
    ui_status_message.content = (
        f"Found {len(search_results)} results. Reading over them now..."
    )
    await ui_status_message.update()

    # Load search result pages
    try:
        documents = CustomWebReader().load_data(urls=search_results)
    except Exception as e:
        dprint(f"Error loading data from URLs: {e}")
        documents = []

    ui_status_message.content = (
        f"Reviewing each of the {len(search_results)} results closely..."
    )
    await ui_status_message.update()

    # Create an index from the documents
    index = VectorStoreIndex.from_documents(documents)
    dprint(f"Created VectorStoreIndex")
    # Create a query engine
    query_engine = index.as_query_engine()
    rag_prompt = FN_CALL_RAG_PROMPT.format(llm_prompt)
    dprint(f"rag_prompt: {rag_prompt}")
    rag_response = str(query_engine.query(rag_prompt))
    dprint(f"rag_response: {rag_response}")

    ui_status_message.content = rag_response
    await ui_status_message.update()

    return rag_response


@traceable
@cl.on_chat_start
async def handle_chat_start():
    message_history = [{"role": "system", "content": FN_CALL_SYSTEM_PROMPT}]
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
        rag_response = await search_and_process(
            search_query, llm_prompt, status_message
        )
        # Update the message history with the RAG response
        message_history.append({"role": "assistant", "content": rag_response})

    elif response.get("content"):
        message_history.append({"role": "assistant", "content": response["content"]})

    dprint(f"message_history: {message_history}")
    cl.user_session.set("message_history", message_history)


if __name__ == "__main__":
    from chainlit.cli import run_chainlit

    run_chainlit(__file__)
