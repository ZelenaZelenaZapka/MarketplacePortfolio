from django.shortcuts import render


def pay_render(request):
    return render(request, "pay_page/main_pay.html")


