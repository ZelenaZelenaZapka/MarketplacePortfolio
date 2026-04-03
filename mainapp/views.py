from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from .forms import RegisterUserForm
from .models import Customer, Seller
from django.utils.text import slugify

def store_page(request):
    return render(request, "page_of_store/startpage.html")

def register_view(request):
    if request.method == "POST":
        form = RegisterUserForm(request.POST)

        if form.is_valid():
            name = form.cleaned_data["name"]
            email = form.cleaned_data["email"]
            phone = form.cleaned_data["phone"]
            password = form.cleaned_data["password"]
            role = form.cleaned_data["role"]

            user = User.objects.create_user(
                username=email,
                email=email,
                password=password,
                first_name=name,
            )

            if role == "buyer":
                Customer.objects.create(
                    user=user,
                    phone=phone,
                    slug=slugify(email),
                )
            else:
                Seller.objects.create(
                    user=user,
                    phone=phone,
                    slug=slugify(email),
                )

            print("Користувача створено")
            return redirect("/store")
    else:
        form = RegisterUserForm()

    return render(request, "auth_page/auth.html", {"form": form})