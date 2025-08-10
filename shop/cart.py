from decimal import Decimal
from typing import Dict, Any

CART_SESSION_KEY = "cart"


def get_cart(request) -> Dict[str, Any]:
    return request.session.get(CART_SESSION_KEY, {})


def save_cart(request, cart: Dict[str, Any]):
    request.session[CART_SESSION_KEY] = cart
    request.session.modified = True


def clear_cart(request):
    if CART_SESSION_KEY in request.session:
        del request.session[CART_SESSION_KEY]
        request.session.modified = True


def add_item(request, product, quantity: int):
    cart = get_cart(request)
    pid = str(product.id)
    item = cart.get(pid, {
        "name": product.name,
        "unit_price": str(product.price),  # store as string to keep session JSON-serializable
        "quantity": 0,
        "image_url": product.image_url,
    })
    item["quantity"] = int(item.get("quantity", 0)) + int(quantity)
    cart[pid] = item
    save_cart(request, cart)


def update_item(request, product_id: int, quantity: int):
    cart = get_cart(request)
    pid = str(product_id)
    if pid in cart:
        if quantity <= 0:
            del cart[pid]
        else:
            cart[pid]["quantity"] = int(quantity)
        save_cart(request, cart)


def remove_item(request, product_id: int):
    cart = get_cart(request)
    pid = str(product_id)
    if pid in cart:
        del cart[pid]
        save_cart(request, cart)


def cart_items_detailed(request):
    """Resolve cart to product objects and totals."""
    from .models import Product
    cart = get_cart(request)
    items = []
    subtotal = Decimal("0.00")
    for pid, data in cart.items():
        try:
            p = Product.objects.get(pk=int(pid))
        except Product.DoesNotExist:
            # remove stale
            continue
        unit_price = Decimal(str(data.get("unit_price", p.price)))
        qty = int(data.get("quantity", 0))
        line_total = unit_price * qty
        subtotal += line_total
        items.append({
            "product": p,
            "quantity": qty,
            "unit_price": unit_price,
            "line_total": line_total,
        })
    return items, subtotal

