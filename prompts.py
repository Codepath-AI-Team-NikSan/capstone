INITIAL_SYSTEM_PROMPT = """
Determine if the user is asking for a product recommendation, prompt the user to provide the type of product user is looking for, price range and features required
. 

Respond with a JSON object containing:
'is_recommendation_query' (boolean) 
'product_type' (string)
'max_price' (integer) if the user specifies a maximum price or None if the user does not specify a maximum price.
'features' (string)
"""
