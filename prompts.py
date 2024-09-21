INITIAL_SYSTEM_PROMPT = """
Determine if the user is asking for a product recommendation. 

Respond with a JSON object containing:
'is_recommendation_query' (boolean) 
'product_type' (string)
'max_price' (integer) if the user specifies a maximum price or None if the user does not specify a maximum price.
"""
