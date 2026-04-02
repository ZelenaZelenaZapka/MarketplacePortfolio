from django.shortcuts import render
from .models import Product

def index(request):
    return render(request, "page_of_store/startpage.html")

# def product_list(request):
#     product = Product.objects.all()
#     return render(request, )
