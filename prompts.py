INITIAL_SYSTEM_PROMPT = """
Determine if the user is asking for a product recommendation. If the user is asking for a product recommendation, prompt the user to provide the type of product user is looking for, price range and features required.

Respond with a JSON object containing:
'is_recommendation_query' (boolean) 
'product_type' (string) if the user specifies a product type or "" if the user does not specify a product type.
'max_price' (integer) if the user specifies a maximum price or 0 if the user does not specify a maximum price.
'features' (string)
"""

SEARCH_RESULT_PROMPT = """
What are the top three {} with a price range of {} that have features {}?

List the top three recommendations with a numbered list. Under each recommendation, write a single sentence with a maximum of 250 characters explaining why you chose it. Make sure you include the price of each item.
"""
