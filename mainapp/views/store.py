from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from ..models import Product, Customer
from .order import get_cart_data


def store_page(request):
    products = Product.objects.all()
    return render(request, "page_of_store/startpage.html", {'products': products, 'cart_item': get_cart_data(request)})


def dashboard(request):
    return render(request, "page_of_store/dashboard.html")


