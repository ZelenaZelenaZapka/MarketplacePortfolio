from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils.text import slugify

from ..models import Seller, Store, Product
from ..forms import ProductForm

@login_required
def dashboard(request):
    try:
        seller = Seller.objects.get(user=request.user)
    except Seller.DoesNotExist:
        return redirect("/store")

    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        description = request.POST.get("description", "").strip()

        if name:
            base_slug = slugify(name)
            slug = base_slug
            counter = 1

            while Store.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1

            Store.objects.create(
                seller_by=seller,
                name=name,
                description=description,
                slug=slug,
            )

        return redirect("dashboard")

    stores = seller.stores.all()

    store_id = request.GET.get("store")
    selected_store = None

    if store_id:
        selected_store = stores.filter(id=store_id).first()

    if not selected_store:
        selected_store = stores.first()

    if selected_store:
        products = selected_store.products.all()
    else:
        products = Product.objects.none()

    product_form = ProductForm()

    return render(
        request,
        "page_of_store/dashboard.html",
        {
            "stores": stores,
            "selected_store": selected_store,
            "products": products,
            "product_form": product_form,
        },
    )


@login_required
def item(request):
    try:
        seller = Seller.objects.get(user=request.user)
    except Seller.DoesNotExist:
        return redirect("/store")

    if request.method != "POST":
        return redirect("dashboard")

    product_form = ProductForm(request.POST, request.FILES)
    store_id = request.POST.get("store_id")

    selected_store = None
    if store_id:
        selected_store = seller.stores.filter(id=store_id).first()

    if not selected_store:
        return redirect("dashboard")

    if product_form.is_valid():
        product = product_form.save(commit=False)
        product.store = selected_store
        product.save()
        return redirect(f"/dashboard?store={selected_store.id}")

    stores = seller.stores.all()
    products = selected_store.products.all()

    return render(
        request,
        "page_of_store/dashboard.html",
        {
            "stores": stores,
            "selected_store": selected_store,
            "products": products,
            "product_form": product_form,
        },
    )

@login_required
def delete_product(request, product_id):
    try:
        seller = Seller.objects.get(user=request.user)
    except Seller.DoesNotExist:
        return redirect("/store")

    if request.method != "POST":
        return redirect("dashboard")

    product = Product.objects.filter(
        id=product_id,
        store__seller_by=seller
    ).select_related("store").first()

    if not product:
        return redirect("dashboard")

    store_id = product.store.id
    product.delete()

    return redirect(f"/dashboard?store={store_id}")

@login_required
def edit_product(request, product_id):
    try:
        seller = Seller.objects.get(user=request.user)
    except Seller.DoesNotExist:
        return redirect("/store")

    product = Product.objects.filter(
        id=product_id,
        store__seller_by=seller
    ).select_related("store").first()

    if not product:
        return redirect("dashboard")

    if request.method != "POST":
        return redirect(f"/dashboard?store={product.store.id}")

    product_form = ProductForm(request.POST, request.FILES, instance=product)

    if product_form.is_valid():
        updated_product = product_form.save(commit=False)
        updated_product.store = product.store
        updated_product.save()
        return redirect(f"/dashboard?store={product.store.id}")

    stores = seller.stores.all()
    selected_store = product.store
    products = selected_store.products.all()

    return render(
        request,
        "page_of_store/dashboard.html",
        {
            "stores": stores,
            "selected_store": selected_store,
            "products": products,
            "product_form": ProductForm(),
            "edit_form_errors_product_id": product.id,
            "edit_form": product_form,
        },
    )