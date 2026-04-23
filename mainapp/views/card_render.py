from django.shortcuts import render

def cart_product_render(request):
    return render(request, "card_of_product/main.html")