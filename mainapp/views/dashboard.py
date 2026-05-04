import json
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils.text import slugify
from django.db.models import Sum, F

from ..models import Seller, Store, Product, Order, OrderItem
from ..forms import ProductForm

# ==============================================================================
# 🔍 ДОПОМІЖНІ ФУНКЦІЇ (Бізнес-логіка)
# ==============================================================================

def _get_active_seller(request):
    """Безпечно отримує продавця або повертає None."""
    return Seller.objects.filter(user=request.user).first()


def _get_selected_store(seller, store_id=None):
    """Визначає поточний магазин для відображення."""
    stores = seller.stores.all()
    return stores.filter(id=store_id).first() if store_id else stores.first()


def _filter_products(products_qs, request):
    """Застосовує фільтри з GET-параметрів до QuerySet товарів."""
    qs = products_qs
    
    # 1. Пошук по назві
    search = request.GET.get('product_name', '').strip()
    if search:
        qs = qs.filter(name__icontains=search)

    # 2. Ціна (від / до)
    price_min = request.GET.get('price_from')
    price_max = request.GET.get('price_to')
    try:
        if price_min:
            qs = qs.filter(price__gte=float(price_min))
        if price_max:
            qs = qs.filter(price__lte=float(price_max))
    except ValueError:
        pass

    # 3. Сортування
    sort = request.GET.get('price_sort')
    if sort == 'asc':
        qs = qs.order_by('price')
    elif sort == 'desc':
        qs = qs.order_by('-price')
    else:
        qs = qs.order_by('-created_at')

    # 4. Тільки в наявності
    if request.GET.get('in_stock'):
        qs = qs.filter(is_active=True)

    return qs


def _build_dashboard_context(seller, store_id=None, extra_context=None, request=None):
    """Збирає всі дані для рендерингу шаблону дашборду."""
    stores = seller.stores.all()
    selected_store = _get_selected_store(seller, store_id)

    # Базовий набір продуктів
    if selected_store:
        products = selected_store.products.all()
        # ЗАСТОСОВУЄМО ФІЛЬТРИ (якщо є request)
        if request:
            products = _filter_products(products, request)
    else:
        products = Product.objects.none()

    # Статистика
    orders_count = 0
    revenue = 0.0
    if selected_store:
        orders_count = Order.objects.filter(
            items__product__store=selected_store
        ).distinct().count()
        
        revenue_data = OrderItem.objects.filter(
            product__store=selected_store
        ).aggregate(total=Sum(F('price') * F('quantity')))
        revenue = revenue_data['total'] or 0.0

    context = {
        "stores": stores,
        "selected_store": selected_store,
        "products": products,
        "product_form": ProductForm(),
        "orders_count": orders_count,
        "revenue": revenue,
    }
    if extra_context:
        context.update(extra_context)
    return context


def _generate_unique_slug(name):
    """Генерує унікальний slug для магазину з лічильником."""
    base_slug = slugify(name)
    slug = base_slug
    counter = 1
    while Store.objects.filter(slug=slug).exists():
        slug = f"{base_slug}-{counter}"
        counter += 1
    return slug


# ==============================================================================
# ⚡ ОБРОБНИКИ ДІЙ (Action Handlers)
# ==============================================================================

def _handle_create_store(request, seller):
    """Створення магазину."""
    name = request.POST.get("name", "").strip()
    description = request.POST.get("description", "").strip()
    if name:
        Store.objects.create(
            seller_by=seller, name=name, description=description, 
            slug=_generate_unique_slug(name)
        )
    return redirect("dashboard")


def _handle_create_product(request, seller):
    """Додавання товару в магазин."""
    store_id = request.POST.get("store_id")
    selected_store = seller.stores.filter(id=store_id).first()
    if not selected_store:
        return redirect("dashboard")

    product_form = ProductForm(request.POST, request.FILES)
    if product_form.is_valid():
        attributes_raw = request.POST.get("attributes_json", "").strip()
        try:
            attributes = json.loads(attributes_raw) if attributes_raw else {}
        except json.JSONDecodeError:
            product_form.add_error(None, "Некоректний JSON характеристик товару.")
            return render(
                request,
                "page_of_store/dashboard.html",
                _build_dashboard_context(
                    seller,
                    store_id,
                    {"product_form": product_form},
                    request=request,
                ),
            )

        product = product_form.save(commit=False)
        product.store = selected_store
        product.attributes = attributes if isinstance(attributes, dict) else {}
        product.save()
        return redirect(f"/dashboard?store={selected_store.id}")

    return render(request, "page_of_store/dashboard.html", 
                  _build_dashboard_context(seller, store_id, 
                                           {"product_form": product_form}, 
                                           request=request))


def _handle_delete_product(request, seller, product_id):
    """Видалення товару."""
    product = Product.objects.filter(
        id=product_id, store__seller_by=seller
    ).select_related("store").first()
    if not product: 
        return redirect("dashboard")
    product.delete()
    return redirect(f"/dashboard?store={product.store.id}")


def _handle_update_product(request, seller, product_id):
    """Оновлення товару."""
    product = Product.objects.filter(
        id=product_id, store__seller_by=seller
    ).select_related("store").first()
    if not product: 
        return redirect("dashboard")

    product_form = ProductForm(request.POST, request.FILES, instance=product)
    if product_form.is_valid():
        attributes_raw = request.POST.get("attributes_json", "").strip()
        try:
            attributes = json.loads(attributes_raw) if attributes_raw else {}
        except json.JSONDecodeError:
            product_form.add_error(None, "Некоректний JSON характеристик товару.")
            return render(request, "page_of_store/dashboard.html",
                          _build_dashboard_context(seller, product.store.id, {
                              "product_form": ProductForm(),
                              "edit_form": product_form,
                              "edit_form_errors_product_id": product.id
                          }, request=request))

        updated = product_form.save(commit=False)
        updated.store = product.store
        updated.attributes = attributes if isinstance(attributes, dict) else {}
        updated.save()
        return redirect(f"/dashboard?store={product.store.id}")

    return render(request, "page_of_store/dashboard.html",
                  _build_dashboard_context(seller, product.store.id, {
                      "product_form": ProductForm(),
                      "edit_form": product_form,
                      "edit_form_errors_product_id": product.id
                  }, request=request))


# ==============================================================================
# 🖥 ЄДИНИЙ VIEW / КОНТРОЛЕР
# ==============================================================================

@login_required
def seller_dashboard(request, product_id=None):
    seller = _get_active_seller(request)
    if not seller:
        return redirect("/store")

    # 🟢 POST-маршрутизація (дії)
    if request.method == "POST":
        action = request.POST.get("action")
        if action == "create_store":
            return _handle_create_store(request, seller)
        if action == "create_product":
            return _handle_create_product(request, seller)
        if action == "delete_product":
            return _handle_delete_product(request, seller, product_id)
        if action == "edit_product":
            return _handle_update_product(request, seller, product_id)
        return redirect("dashboard")

    # 🔵 GET-запит (перегляд + фільтри)
    store_id = request.GET.get("store")
    return render(request, "page_of_store/dashboard.html", 
                  _build_dashboard_context(seller, store_id, request=request))

