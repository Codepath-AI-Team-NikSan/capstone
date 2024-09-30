import time

from langfuse import Langfuse
import openai
from dotenv import load_dotenv
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from async_web_reader import AsyncWebReader
import asyncio
from search_handler import Provider, search

load_dotenv()

langfuse = Langfuse()


def llm_evaluation(output, expected_output):
    client = openai.OpenAI()

    prompt = f"""
    Compare the following output and see if the output recommends a product with details:

    Output: {output}

    Provide a score (0 for incorrect, 1 for correct) and a brief reason for your evaluation.
    Return your response in the following JSON format:
    {{
        "score": 0 or 1,
        "reason": "Your explanation here"
    }}
    """

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are an AI assistant tasked with evaluating the accuracy of responses."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.2
    )

    evaluation = response.choices[0].message.content
    result = eval(evaluation)  # Convert the JSON string to a Python dictionary

    # Debug printout
    print(f"Output: {output}")
    print(f"Expected Output: {expected_output}")
    print(f"Evaluation Result: {result}")

    return result["score"], result["reason"]


from datetime import datetime


def rag_query(query_engine, input):
    generationStartTime = datetime.now()

    response = query_engine.query(input)
    output = response.response
    print(output)

    langfuse_generation = langfuse.generation(
        name="strategic-plan-qa",
        input=input,
        output=output,
        model="gpt-3.5-turbo",
        start_time=generationStartTime,
        end_time=datetime.now()
    )

    return output, langfuse_generation

async def run_experiment(experiment_name):
    dataset = langfuse.get_dataset("product_recommendation_qa_pairs")
    for item in dataset.items:
        documents = []
        search_results = search(
            search_query=item.input, provider=Provider.DuckDuckGo, fetch_docs=False, max_results=10
        )
        if search_results:
            try:
                reader = AsyncWebReader()
                documents = await reader.load_data(urls=search_results)
            except Exception as e:
                documents = []
        # print(documents)
        if documents:
            index = VectorStoreIndex.from_documents(documents)
            query_engine = index.as_query_engine()
            completion, langfuse_generation = rag_query(query_engine, item.input)
            item.link(langfuse_generation, experiment_name)  # pass the observation/generation object or the id
            score, reason = llm_evaluation(completion, item.expected_output)
            langfuse_generation.score(
                name="accuracy",
                value=score,
                comment=reason
            )
        time.sleep(15)


asyncio.run(run_experiment("Experiment 2"))