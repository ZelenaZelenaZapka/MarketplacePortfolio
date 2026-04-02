from django.shortcuts import render
from .models import Product

def index(request):
    return render(request, "page_of_store/startpage.html")

def reg_page(request):
    return render(request, "auth_page/auth.html")
