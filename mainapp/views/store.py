from django.shortcuts import render, redirect
from django.contrib.auth import logout
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Count, Sum, F
from django.http import JsonResponse
from ..models import Product, Customer, Order, Category, Seller, Store, OrderItem
from .order import get_cart_data

def get_filtered_products(request):
    qs = Product.objects.select_related('category', 'store')
    
    search = request.GET.get('search', '').strip()
    if search:
        qs = qs.filter(name__icontains=search)

    search_store = request.GET.get('search_store', '').strip()
    if search_store:
        qs = qs.filter(store__name__icontains=search_store)

    category_id = request.GET.get('category')
    if category_id:
        qs = qs.filter(category_id=category_id)

    price_min = request.GET.get('price_min')
    price_max = request.GET.get('price_max')
    try:
        if price_min: qs = qs.filter(price__gte=float(price_min))
        if price_max: qs = qs.filter(price__lte=float(price_max))
    except ValueError:
        pass

    if request.GET.get('new') in ('true', '1', 'on'): qs = qs.filter(is_active=True)
    if request.GET.get('sale') in ('true', '1', 'on'): qs = qs.filter(has_discount=True)

    return qs.order_by('-created_at')



def get_recent_purchased_products(user):
    if not user.is_authenticated:
        return []
    try:
        customer = user.customer
        recent_orders = customer.orders.order_by('-created_at')[:5] \
            .prefetch_related('items__product', 'items__product__store')
        
        seen_ids = set()
        recent_purchased = []
        for order in recent_orders:
            for item in order.items.all():
                if item.product_id not in seen_ids:
                    recent_purchased.append(item.product)
                    seen_ids.add(item.product_id)
                if len(recent_purchased) >= 2:
                    break
            if len(recent_purchased) >= 2:
                break
        return recent_purchased
    except ObjectDoesNotExist:
        return []


def get_seller_dashboard_data(request):
    if not request.user.is_authenticated:
        return {'is_seller': False}
    try:
        seller = Seller.objects.get(user=request.user)
        user_stores = Store.objects.filter(seller_by=seller)
        if not user_stores.exists():
            return {'is_seller': True, 'no_stores': True}

        selected_store_id = request.GET.get('store_id')
        current_store = user_stores.filter(id=selected_store_id).first() or user_stores.first()

        products_count = Product.objects.filter(store=current_store).count()
        orders_count = Order.objects.filter(items__product__store=current_store).distinct().count()
        revenue = OrderItem.objects.filter(product__store=current_store).aggregate(total=Sum(F('price') * F('quantity')))['total'] or 0

        top_product_data = OrderItem.objects.filter(product__store=current_store) \
            .values('product__name') \
            .annotate(total_sold=Sum('quantity')) \
            .order_by('-total_sold') \
            .first()

        if top_product_data:
            top_product_name = top_product_data['product__name']
            top_product_count = top_product_data['total_sold']
        else:
            top_product_name = "Немає продажів"
            top_product_count = 0

        return {
            'is_seller': True,
            'stores': user_stores,
            'current_store': current_store,
            'products_count': products_count,
            'orders_count': orders_count,
            'revenue': revenue,
            'top_product_name': top_product_name,
            'top_product_count': top_product_count,
        }
    except Seller.DoesNotExist:
        return {'is_seller': False}


def store_page(request):
    products = get_filtered_products(request)
    cart_data = get_cart_data(request)
    recent_purchased_products = get_recent_purchased_products(request.user)
    seller_data = get_seller_dashboard_data(request)
    
    context = {
        'products': products,
        'categories': Category.objects.all(),
        'cart_item': cart_data,
        'is_seller': seller_data.get('is_seller', False),
        'recent_purchased_products': recent_purchased_products,
        **seller_data,
    }

    if request.META.get('HTTP_HX_REQUEST'):
        if 'store_id' in request.GET:
            return render(request, "page_of_store/_seller_stats.html", context)
        return render(request, "page_of_store/_product_grid.html", context)

    return render(request, "page_of_store/startpage.html", context)


def logout_view(request):
    logout(request)
    return redirect("")