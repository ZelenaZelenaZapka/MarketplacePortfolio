from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.views.decorators.http import require_POST

from ..models import Product, Customer, Cart, CartItem


def _get_customer(request):
    if not request.user.is_authenticated:
        return None
    return Customer.objects.filter(user=request.user).first()

# якщо Cart для цього customer уже є → повертає його
def _get_or_create_cart(customer):
    cart, _ = Cart.objects.get_or_create(customer=customer)
    return cart


def get_cart_data(request):
    """
    Return cart data in a unified format for:
      - guests: session['cart'] = { "product_id": quantity }
      - logged in: Cart + CartItem in DB
    """
    # AUTH -> DB
    if request.user.is_authenticated:
        customer = _get_customer(request)
        if not customer:
            return {"cart_items": [], "cart_count": 0, "total_price": 0.0}

        cart = Cart.objects.filter(customer=customer).first() # SELECT * FROM cart WHERE customer_id = <id> LIMIT 1;
        if not cart:
            return {"cart_items": [], "cart_count": 0, "total_price": 0.0}


        """
        N+1 problem: when you load a list of objects and then in a loop access related data,
        Django may run 1 query for the list + 1 extra query per element (so N extra queries).
        We later use select_related/prefetch_related to fetch related data in advance and avoid many DB hits.
        """


        items = cart.items.select_related("product").all()

        cart_items = []
        total_price = 0
        cart_count = 0

        for item in items:
            product = item.product
            quantity = item.quantity
            item_total = product.price * quantity

            cart_items.append({
                "id": product.id,
                "name": product.name,
                "price": float(product.price),
                "quantity": quantity,
                "item_total": float(item_total),
                "image_url": product.image.url if getattr(product, "image", None) and product.image else "",
            })

            total_price += item_total
            cart_count += quantity

        return {
            "cart_items": cart_items,
            "cart_count": cart_count,
            "total_price": float(total_price),
        }

    # GUEST -> SESSION
    cart = request.session.get("cart", {})
    products = Product.objects.filter(id__in=cart.keys())

    cart_items = []
    total_price = 0
    cart_count = 0

    for product in products:
        quantity = int(cart.get(str(product.id), 0))
        item_total = product.price * quantity

        cart_items.append({
            "id": product.id,
            "name": product.name,
            "price": float(product.price),
            "quantity": quantity,
            "item_total": float(item_total),
            "image_url": product.image.url if getattr(product, "image", None) and product.image else "",
        })

        total_price += item_total
        cart_count += quantity

    return {
        "cart_items": cart_items,
        "cart_count": cart_count,
        "total_price": float(total_price),
    }



@require_POST
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    # AUTH -> DB
    if request.user.is_authenticated:
        customer = _get_customer(request)
        if not customer:
            return JsonResponse({"success": False, "error": "Customer not found"}, status=400)

        cart = _get_or_create_cart(customer)

        item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={"quantity": 1},
        )
        if not created:
            item.quantity += 1
            item.save(update_fields=["quantity"])

        cart_count = sum(ci.quantity for ci in cart.items.all())

        return JsonResponse({
            "success": True,
            "product_id": product.id,
            "product_name": product.name,
            "quantity": item.quantity,
            "cart_count": cart_count,
        })

    # GUEST -> SESSION
    if not request.session.session_key:
        request.session.create()

    guest_cart = request.session.get("cart", {})
    product_id = str(product.id)

    current_qty = int(guest_cart.get(product_id, 0))
    guest_cart[product_id] = current_qty + 1

    request.session["cart"] = guest_cart # save data in session
    request.session.modified = True # say to Django "session changed please save"

    return JsonResponse({
        "success": True,
        "product_id": product.id,
        "product_name": product.name,
        "quantity": guest_cart[product_id],
        "cart_count": sum(guest_cart.values()),
    })


def cart_data(request):
    return JsonResponse({
        "success": True,
        **get_cart_data(request),
    })


def cart_detail(request):
    customer = _get_customer(request)

    items_qs = []
    if request.user.is_authenticated and customer:
        cart = Cart.objects.filter(customer=customer).first()
        if cart:
            items_qs = cart.items.select_related("product")

    data = get_cart_data(request)
    context = {
        **data,
        "items_qs": items_qs,  # <-- queryset з CartItem
        "customer": customer,
        "is_guest": not request.user.is_authenticated,
    }
    return render(request, "page_of_store/cart_detail.html", context)


@require_POST
def remove_from_cart(request, product_id):
    # AUTH -> DB
    if request.user.is_authenticated:
        customer = _get_customer(request)
        if not customer:
            return JsonResponse({"success": False, "error": "Customer not found"}, status=400)

        cart = Cart.objects.filter(customer=customer).first()
        if cart:
            CartItem.objects.filter(cart=cart, product_id=product_id).delete()

        return JsonResponse({"success": True})

    # GUEST -> SESSION
    cart = request.session.get("cart", {})
    pid = str(product_id)
    if pid in cart:
        del cart[pid]
        request.session["cart"] = cart
        request.session.modified = True

    return JsonResponse({"success": True})
