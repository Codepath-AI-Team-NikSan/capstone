import json
import os

WISHLIST_FILE = "wishlist.json"


def load_wishlist():
    if os.path.exists(WISHLIST_FILE):
        with open(WISHLIST_FILE, "r") as file:
            return json.load(file)
    return []


def save_wishlist(wishlist):
    with open(WISHLIST_FILE, "w") as file:
        json.dump(wishlist, file, indent=4)


def add_to_wishlist(name, price, description, sources, buy_links):
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
    return f"✅ Added to your wishlist: {name}"


def get_wishlist(wishlist_str=False):
    """Get the entire wishlist."""
    wishlist = load_wishlist()
    if wishlist_str:
        response = "\n"
        if wishlist:
            count = 1
            for wishlist_entry in wishlist:
                response += f"\nItem {count}\nName: {wishlist_entry['name']}"
                response += f"\nPrice: {wishlist_entry['price']}"
                response += f"\nDescription: {wishlist_entry['description']}"
                response += f"\nSources: {wishlist_entry['sources']}"
                response += f"\nBuy Links: {wishlist_entry['buy_links']}"
                response += f"\n\n"
                count += 1
        else:
            response = f"\n🫙 Your wishlist is empty!"
        return response
    else:
        return wishlist


def remove_from_wishlist(name):
    """Remove an item from the wishlist by name."""
    wishlist = load_wishlist()
    new_wishlist = [
        item for item in wishlist if name.lower() not in item["name"].lower()
    ]

    if len(new_wishlist) < len(wishlist):
        save_wishlist(new_wishlist)
        return f"❌ Removed from your wishlist: {name}"
    else:
        return f"Item not found in wishlist: {name}"
