from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from ..models import Product, Customer


def store_page(request):
    products = Product.objects.all()
    return render(request, "page_of_store/startpage.html", {'products': products})


def dashboard(request):
    return render(request, "page_of_store/dashboard.html")


def get_cart_data(request):
    cart = request.session.get('cart', {})
    products = Product.objects.filter(id__in=cart.keys())

    cart_items = []
    total_price = 0
    cart_count = 0

    for product in products:
        quantity = cart.get(str(product.id), 0)
        item_total = product.price * quantity

        cart_items.append({
            'id': product.id,
            'name': product.name,
            'price': float(product.price),
            'quantity': quantity,
            'item_total': float(item_total),
            'image_url': product.image.url if getattr(product, 'image', None) and product.image else '',
        })

        total_price += item_total
        cart_count += quantity

    return {
        'cart_items': cart_items,
        'cart_count': cart_count,
        'total_price': float(total_price),
    }


def add_to_cart(request, product_id):
    if request.method == "POST":
        product = get_object_or_404(Product, id=product_id)

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


def cart_data(request):
    return JsonResponse({
        'success': True,
        **get_cart_data(request)
    })


def cart_detail(request):
    cart_data = get_cart_data(request)

    customer = None
    if request.user.is_authenticated:
        customer = Customer.objects.filter(user=request.user).first()

    context = {
        **cart_data,
        'customer': customer,
        'is_guest': not request.user.is_authenticated,
    }

    return render(request, 'page_of_store/cart_detail.html', context)

def remove_from_cart(request, product_id):
    if request.method == "POST":
        cart = request.session.get('cart', {})
        product_id_str = str(product_id)

        if product_id_str in cart:
            del cart[product_id_str]
            request.session['cart'] = cart
            request.session.modified = True

        return JsonResponse({'success': True})

    return JsonResponse({'success': False, 'error': 'Invalid request'}, status=400)