from django.shortcuts import render
from .order import get_cart_data

def pay_render(request):
    data = get_cart_data(request)
    return render(request, "pay_page/main_pay.html", context=data)


