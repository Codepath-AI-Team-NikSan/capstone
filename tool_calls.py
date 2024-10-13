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
                    "description": "The query used to search Google for relevant product reviews and recommendations.",
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


ADD_TO_WISH_LIST_TOOL = {
    "type": "function",
    "function": {
        "name": "add_to_wishlist",
        "description": "User will be able to add products to a wishlist to recall at a later time",
        "parameters": {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "Name of the product",
                },
                "price": {
                    "type": "string",
                    "description": "Price of the product"
                },
                "description": {
                    "type": "string",
                    "description": "Description of the product, contains the features, pros and cons"
                },
                "sources": {
                    "type": "string",
                    "description": "Sources for the review"
                },
                "buy_links": {
                    "type": "string",
                    "description": "Description of the product, contains the features, pros and cons"
                },
            },
            "required": ["name","price","description", "sources"],
            "additionalProperties": False,
        },
    },
}

GET_WISH_LIST_TOOL = {
    "type": "function",
    "function": {
        "name": "get_wishlist",
        "description": "Get wishlist"
    },
}

REMOVE_FROM_WISH_LIST_TOOL = {
    "type": "function",
    "function": {
        "name": "remove_from_wishlist",
        "description": "User remove products from the wishlist",
        "parameters": {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "Name of the product, resolve to the full name of the product if required",
                }
            },
            "required": ["name"],
            "additionalProperties": False,
        },
    },
}


ADD_TO_ORDER_TOOL = {
    "type": "function",
    "function": {
        "name": "add_to_orders",
        "description": "Allow the user to order the product or checkout the product, if quantity is not mentioned assume quantity as one",
        "parameters": {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "Name of the product",
                },
                "price": {
                    "type": "string",
                    "description": "Price of the product"
                },
                "description": {
                    "type": "string",
                    "description": "Description of the product, contains the features, pros and cons"
                },
                "quantity": {
                    "type": "number",
                    "description": "Quantity"
                },
            },
            "required": ["name","price","description", "quantity"],
            "additionalProperties": False,
        },
    },
}

GET_ORDERS_TOOL = {
    "type": "function",
    "function": {
        "name": "get_orders",
        "description": "Get Orders"
    },
}