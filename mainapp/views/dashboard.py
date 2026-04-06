from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils.text import slugify

from ..models import Seller, Store
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

    return render(
        request,
        "page_of_store/dashboard.html",
        {
            "stores": stores,
        },
    )

@login_required
def item(request):
    product_form = ProductForm()

    if request.method == 'POST':
        product_form = ProductForm(request.POST, request.FILES)
        print("ITEM VIEW WORKS")
        print(request.POST)
        print(request.FILES)

        if product_form.is_valid():
            product = product_form.save(commit=False)
            product.store = Store.objects.first()   # тимчасово
            product.save()
            return redirect('dashboard')
        else:
            print(product_form.errors)

    return render(request, 'page_of_store/dashboard.html', {
        'product_form': product_form,
    })

