import json
import os

WISHLIST_FILE = "wishlist.json"


def load_wishlist():
    """
    Load the wishlist from the JSON file.

    Returns:
        list: A list of wishlist items, each represented as a dictionary.
              If the file does not exist or is empty, returns an empty list.
    """
    if os.path.exists(WISHLIST_FILE):
        try:
            with open(WISHLIST_FILE, "r") as file:
                return json.load(file)
        except json.JSONDecodeError:
            # If the JSON is malformed, return an empty list.
            return []
    return []


def save_wishlist(wishlist):
    """
    Save the wishlist to the JSON file.

    Args:
        wishlist (list): A list of wishlist items to save, each represented as a dictionary.
    """
    with open(WISHLIST_FILE, "w") as file:
        json.dump(wishlist, file, indent=4)


def add_to_wishlist(name, price, description, sources, buy_links):
    """
    Add a new item to the wishlist and save the updated list.

    Args:
        name (str): The name of the item.
        price (float): The price of the item.
        description (str): A brief description of the item.
        sources (list): A list of sources or places where the item can be purchased.
        buy_links (list): A list of URLs where the item can be bought.

    Returns:
        str: A message indicating that the item was added to the wishlist.
    """
    wishlist = load_wishlist()
    item = {
        "name": name,
        "price": price,
        "description": description,
        "sources": sources,
        "buy_links": buy_links,
    }
    wishlist.append(item)
    save_wishlist(wishlist)
    return f"✅ Added to wishlist: {name}"


def get_wishlist(as_string=False):
    """
    Get the entire wishlist.

    Args:
        as_string (bool): If True, returns the wishlist as a formatted string.
                          If False, returns the wishlist as a list of dictionaries.

    Returns:
        str or list: The wishlist as a formatted string if `as_string` is True,
                     otherwise a list of dictionaries.
    """
    wishlist = load_wishlist()
    if as_string:
        if wishlist:
            response = "\n"
            for index, item in enumerate(wishlist, start=1):
                response += (
                    f"{index}. **{item['name']}**\n"
                    f"Price: {item['price']}\n"
                    f"Description: {item['description']}\n"
                    f"Review Sources: {item['sources']}\n"
                    f"Link(s) to Buy: {item['buy_links']}\n"
                    f"\n"
                )
        else:
            response = "\nWishlist is empty!"
        return response
    else:
        return wishlist


def remove_from_wishlist(name):
    """
    Remove an item from the wishlist by name.

    Args:
        name (str): The name of the item to remove. The search is case-insensitive.

    Returns:
        str: A message indicating whether the item was successfully removed or not found.
    """
    wishlist = load_wishlist()
    new_wishlist = [
        item for item in wishlist if name.lower() not in item["name"].lower()
    ]

    if len(new_wishlist) < len(wishlist):
        save_wishlist(new_wishlist)
        return f"🗑️ Removed from wishlist: {name}"
    else:
        return f"Item not found in wishlist: {name}"
