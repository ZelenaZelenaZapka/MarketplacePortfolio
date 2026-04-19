from django.shortcuts import render, redirect
from django.contrib.auth import logout
from django.core.exceptions import ObjectDoesNotExist
from ..models import Product, Customer, Order, Category
from .order import get_cart_data


def get_filtered_products(request):
    qs = Product.objects.select_related('category')

    search = request.GET.get('search', '').strip()
    if search:
        qs = qs.filter(name__icontains=search)

    category_id = request.GET.get('category')
    if category_id:
        qs = qs.filter(category_id=category_id)

    price_min = request.GET.get('price_min')
    price_max = request.GET.get('price_max')
    if price_min:
        try: qs = qs.filter(price__gte=float(price_min))
        except ValueError: pass
    if price_max:
        try: qs = qs.filter(price__lte=float(price_max))
        except ValueError: pass

    if request.GET.get('new'): 
        qs = qs.filter(is_active=True)

    if request.GET.get('sale'): qs = qs.filter(has_discount=True)
    if request.GET.get('top'): qs = qs.filter(is_top=True)

    return qs.order_by('-created_at')


def get_recent_purchased_products(user):
    if not user.is_authenticated:
        return []

    try:
        customer = user.customer
        orders = customer.orders.order_by('-created_at')[:5] \
            .prefetch_related('items__product', 'items__product__store')

        seen_ids = set()
        products = []
        for order in orders:
            for item in order.items.all():
                if item.product_id not in seen_ids:
                    products.append(item.product)
                    seen_ids.add(item.product_id)
                if len(products) >= 2: break
            if len(products) >= 2: break
        return products
    except ObjectDoesNotExist:
        return []


def store_page(request):
    context = {
        'products': get_filtered_products(request),
        'categories': Category.objects.all(),
        'cart_item': get_cart_data(request),
        'recent_purchased_products': get_recent_purchased_products(request.user),
        'is_seller': request.user.groups.filter(name='seller').exists() if request.user.is_authenticated else False,
    }
    
    if request.META.get('HTTP_HX_REQUEST'):
        return render(request, "page_of_store/_product_grid.html", context)
    
    return render(request, "page_of_store/startpage.html", context)


def logout_view(request):
    logout(request)
    return redirect('')


