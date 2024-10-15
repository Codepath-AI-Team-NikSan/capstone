import json
import os

ORDERS_FILE = 'orders.json'

def load_orders():
    if os.path.exists(ORDERS_FILE):
        with open(ORDERS_FILE, 'r') as file:
            return json.load(file)
    return []


def save_orders(checkout_details):
    with open(ORDERS_FILE, 'w') as file:
        json.dump(checkout_details, file, indent=4)

def add_to_orders(name, price, description, quantity):
    orders = load_orders()
    item = {
        'name': name,
        'price': price,
        'description': description,
        'qty': quantity
    }
    orders.append(item)
    save_orders(orders)
    return(f'Order of item : {name} have been placed')


def get_orders(orders_str=False):
    """Get the entire orders."""
    orders = load_orders()
    if orders_str:
        response = "\n"
        if orders:
            count = 1
            for order in orders:
                response += f"\nItem {count}\nName: {order['name']}"
                response += f"\nPrice: {order['price']}"
                response += f"\nDescription: {order['description']}"
                response += f"\nQuantity: {order['qty']}"
                response += f"\n\n"
                count += 1
        else:
            response = f'\nWishlist Empty!'
        return response
    else:
        return orders