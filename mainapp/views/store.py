from django.shortcuts import render
from django.contrib.auth.decorators import login_required

def store_page(request):
    return render(request, "page_of_store/startpage.html")
