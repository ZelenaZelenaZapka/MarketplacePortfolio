from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from ..models import Product, Customer


def store_page(request):
    products = Product.objects.all()
    return render(request, "page_of_store/startpage.html", {'products': products})


def dashboard(request):
    return render(request, "page_of_store/dashboard.html")


