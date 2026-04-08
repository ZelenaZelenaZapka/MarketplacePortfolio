from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from ..models import Product

def store_page(request):
    products = Product.objects.all()
    return render(request, "page_of_store/startpage.html", {'products': products})

def dashboard(request):
    return render (request, "page_of_store/dashboard.html")
