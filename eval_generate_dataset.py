import time

from dotenv import load_dotenv
from async_web_reader import AsyncWebReader
from search_handler import search, Provider
import  asyncio
from openai import OpenAI
from langfuse import Langfuse
import os
import json


# Load environment variables
load_dotenv()

client = OpenAI()

# Function to generate questions and answers
def generate_qa(prompt, text, temperature=0.2):
    messages = [
            {"role": "system", "content": prompt}]
    if text:
        messages.append({"role": "user", "content": text})
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        temperature=temperature,
        timeout=30
    )

    print(response.choices[0].message.content)

    # Strip extraneous symbols from the response content
    content = response.choices[0].message.content.strip()

    # Remove potential JSON code block markers
    content = content.strip()
    if content.startswith('```'):
        content = content.split('\n', 1)[-1]
    if content.endswith('```'):
        content = content.rsplit('\n', 1)[0]
    content = content.strip()

    # Attempt to parse the cleaned content as JSON
    try:
        parsed_content = json.loads(content.strip())
        return parsed_content
    except json.JSONDecodeError:
        print("Error: Unable to parse JSON. Raw content:")
        print(content)
        return []

generate_question_prompt = """
You are an expert educational content creator tasked with generating factual questions. 
These questions should focus on retrieving product recommendation style of questions where the user is asking for recommendation on some product
based on its price range, characteristics, usability etc. All the generated question should be a form of asking for product recommendation

Instructions:

- Generate **3** factual questions
- Present the output in the following structured JSON format:
[
    "What are the top phones in the market right now for gaming under $1000",
]
"""

factual_prompt = """
You are an expert educational content creator tasked with generating factual questions and answers based on the following document excerpt. 
These questions should focus on retrieving product recommendation style of questions where the user is asking for recommendation on some prodcut
based on its price range, characteristics, usability etc. All the generated question should be a form of asking for product recommendation
based on the document given

Instructions:

- Generate **5** factual questions, each with a corresponding **expected_output**.
- Present the output in the following structured JSON format:

[
  {
    "question": "What are the top phones in the market right now for gaming",
    "expected_output": "The top phones available in the market right for gaming are Samsung and Iphone 16"
  }
]
"""

# Generate dataset
dataset_file = 'qa_dataset.json'
async def get_document(query):
    search_results = search(
        search_query=query, provider=Provider.DuckDuckGo, fetch_docs=True, max_results=10
    )
    if search_results:
        return str(search_results)
    return None


async def fetch_dataset():
    dataset = []
    if os.path.exists(dataset_file):
        # Load dataset from local file if it exists
        with open(dataset_file, 'r') as f:
            dataset = json.load(f)
    else:
        # Generate dataset if local file doesn't exist
        queries = generate_qa(generate_question_prompt, None, temperature=0.2)
        for query in queries:
            print("Searching for "+ query)
            docs = await get_document(query)
            if docs:
                qa_pairs = generate_qa(factual_prompt, docs, temperature=0.2)
                dataset.extend(qa_pairs)
                time.sleep(90)
                print("Writing results to dataset for query " + query)
        print(dataset)
        # Write dataset to local file
        with open(dataset_file, 'w') as f:
            json.dump(dataset, f)
    return dataset

async def main():
    dataset = await fetch_dataset()
    print("Create Dataset in langfuse")
    langfuse = Langfuse()
    dataset_name = "product_recommendation_qa_pairs"
    langfuse.create_dataset(name=dataset_name);

    for item in dataset:
        langfuse.create_dataset_item(
            dataset_name=dataset_name,
            input=item["question"],
            expected_output=item["expected_output"]
        )

# Run the main function
if __name__ == "__main__":
    asyncio.run(main())