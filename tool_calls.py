PRODUCT_SEARCH_TOOL = {
    "type": "function",
    "function": {
        "name": "product_search",
        "description": "Searches Google to find relevant product reviews and recommendations, and then reviews the Google search results to find the best product for the user. Call this once you have enough information from the user to conduct a search.",
        "parameters": {
            "type": "object",
            "properties": {
                "google_search_query": {
                    "type": "string",
                    "description": "The query used to search Google for relevant product reviews and recommendations. Do not include the current year in the search query unless it's relevant to the user's needs.",
                },
                "llm_prompt": {
                    "type": "string",
                    "description": "The natural language prompt used by an LLM to review the Google search results and recommend the top product(s) (up to 3 maximum) to the user based on the user's preferences.",
                },
            },
            "required": ["google_search_query", "llm_prompt"],
            "additionalProperties": False,
        },
    },
}
