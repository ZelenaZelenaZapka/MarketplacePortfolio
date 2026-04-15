from django.shortcuts import render, get_object_or_404, redirect
from ..models import Product, Customer, Order
from .order import get_cart_data
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist


def store_page(request):
    products = Product.objects.all()
    cart_item = get_cart_data(request)
    recent_purchased_products = []

    if request.user.is_authenticated:
        try:
            customer = request.user.customer
            
            # Забираємо останні 5 замовлень + товари + магазини (щоб уникнути N+1)
            recent_orders = customer.orders.order_by('-created_at')[:5] \
                .prefetch_related('items__product', 'items__product__store')
            
            seen_ids = set()
            for order in recent_orders:
                for item in order.items.all():
                    if item.product_id not in seen_ids:
                        recent_purchased_products.append(item.product)
                        seen_ids.add(item.product_id)
                    if len(recent_purchased_products) >= 2:
                        break
                if len(recent_purchased_products) >= 2:
                    break
        except ObjectDoesNotExist:
            pass  # Профілю немає → список порожній

    return render(request, "page_of_store/startpage.html", {
        'products': products,
        'cart_item': cart_item,
        'recent_purchased_products': recent_purchased_products  # ✅ 0, 1 або 2 товари
    })


def dashboard(request):
    return render(request, "page_of_store/dashboard.html")


def logout_view(request):
    logout(request)
    return redirect('')







