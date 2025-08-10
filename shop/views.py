from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.http import HttpResponse
from django.shortcuts import redirect, render, get_object_or_404
from .models import Product, Order, OrderItem
from . import cart as cart_utils


def product_list(request):
    products = Product.objects.order_by("-created_at")
    return render(request, "shop/product_list.html", {"products": products})


def product_detail(request, pk: int):
    product = get_object_or_404(Product, pk=pk)
    return render(request, "shop/product_detail.html", {"product": product})


def cart_view(request):
    items, subtotal = cart_utils.cart_items_detailed(request)
    return render(request, "shop/cart.html", {"items": items, "subtotal": subtotal})


def add_to_cart(request, pk: int):
    product = get_object_or_404(Product, pk=pk)
    qty = int(request.POST.get("quantity", 1)) if request.method == "POST" else 1
    if qty < 1:
        qty = 1
    if product.stock <= 0:
        messages.error(request, "Product out of stock")
        return redirect("product_detail", pk=pk)
    cart_utils.add_item(request, product, qty)
    messages.success(request, f"Added {qty} × {product.name} to cart")
    return redirect("cart_view")


def update_cart(request, pk: int):
    qty = int(request.POST.get("quantity", 1)) if request.method == "POST" else 1
    cart_utils.update_item(request, pk, qty)
    return redirect("cart_view")


def remove_from_cart(request, pk: int):
    cart_utils.remove_item(request, pk)
    return redirect("cart_view")


@login_required
def checkout(request):
    items, subtotal = cart_utils.cart_items_detailed(request)
    if request.method == "POST":
        if not items:
            messages.error(request, "Your cart is empty")
            return redirect("cart_view")
        # create order
        order = Order.objects.create(user=request.user, total_amount=subtotal, status="pending")
        for item in items:
            p = item["product"]
            qty = item["quantity"]
            if p.stock < qty:
                messages.error(request, f"Insufficient stock for {p.name}")
                order.delete()
                return redirect("cart_view")
            OrderItem.objects.create(order=order, product=p, quantity=qty, unit_price=item["unit_price"])
            p.stock -= qty
            p.save(update_fields=["stock"])
        cart_utils.clear_cart(request)
        messages.success(request, f"Order #{order.id} placed!")
        return render(request, "shop/order_confirmation.html", {"order": order})
    return render(request, "shop/checkout.html", {"items": items, "subtotal": subtotal})


def register(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("product_list")
    else:
        form = UserCreationForm()
    return render(request, "shop/register.html", {"form": form})


def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect("product_list")
    else:
        form = AuthenticationForm(request)
    return render(request, "shop/login.html", {"form": form})


def logout_view(request):
    logout(request)
    return redirect("product_list")
