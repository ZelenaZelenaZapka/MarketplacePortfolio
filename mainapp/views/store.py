from contextlib import redirect_stderr

from django.http import JsonResponse

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from ..models import Product

def store_page(request):
    products = Product.objects.all()
    return render(request, "page_of_store/startpage.html", {'products': products})

def dashboard(request):
    return render (request, "page_of_store/dashboard.html")

def add_to_cart(request, product_id):
    if request.method == "POST":
        product = get_object_or_404(Product, id=product_id)
        print("Hello POST request")

        cart = request.session.get('cart', {})
        product_id_str = str(product.id)

        if product_id_str in cart:
            cart[product_id_str] += 1
        else:
            cart[product_id_str] = 1

        request.session['cart'] = cart
        request.session.modified = True

        cart_count = sum(cart.values())

        return JsonResponse({
            'success': True,
            'product_id': product.id,
            'product_name': product.name,
            'quantity': cart[product_id_str],
            'cart_count': cart_count,
        })

    return JsonResponse({'success': False, 'error': 'Invalid request'}, status=400)

def cart_detail(request):
    cart = request.session.get('cart', {})
    products = Product.objects.filter(id__in=cart.keys())

    cart_items = []
    total_price = 0

    for product in products:
        quantity = cart[str(product.id)]
        item_total = product.price * quantity
        total_price += item_total

        cart_items.append({
            'product': product,
            'quantity': quantity,
            'item_total': item_total,
        })

    return render(request, 'startpage.html', {
        'cart_items': cart_items,
        'total_price': total_price,
    })
