from django.shortcuts import render, get_object_or_404
from django.db.models import Sum
from ..models import Product, OrderItem

def cart_product_render(request, item_id):
    product = get_object_or_404(Product, id=item_id)
    
    # 📊 Рахуємо загальну кількість проданих одиниць цього товару
    # Якщо хочеш рахувати тільки підтверджені замовлення, додай: order__status__in=['completed', 'paid']
    sold_data = OrderItem.objects.filter(
        product=product
    ).aggregate(total_sold=Sum('quantity'))
    
    # Якщо замовлень ще не було, Sum поверне None. Захищаємося:
    sold_count = sold_data['total_sold'] or 0
    
    attributes = product.attributes if isinstance(product.attributes, dict) else {}
    specs = [(str(name), str(value)) for name, value in attributes.items() if str(name).strip() and str(value).strip()]

    context = {
        'product': product,
        'sold_count': sold_count,
        'specs': specs,
    }
    return render(request, "card_of_product/main.html", context)