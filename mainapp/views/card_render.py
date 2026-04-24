# views.py
from django.shortcuts import render, get_object_or_404
from ..models import Product  # ← замініть на вашу модель

def cart_product_render(request, item_id):
    # Безпечне отримання об'єкта або 404, якщо не знайдено
    product = get_object_or_404(Product, id=item_id)
    
    context = {
        'product': product,
    }
    return render(request, "card_of_product/main.html", context)