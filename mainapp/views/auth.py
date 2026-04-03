from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.utils.text import slugify

from ..forms import RegisterUserForm
from ..models import Customer, Seller

def register_view(request):
    form = RegisterUserForm()
    login_error = None

    if request.method == "POST":
        form_type = request.POST.get("form_type")

        if form_type == "register":
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

                login(request, user)
                return redirect("/store")
        elif form_type == "login":
            email = request.POST.get("email")
            password = request.POST.get("password")

            user = authenticate(request, username=email, password=password)

            if user is not None:
                login(request, user)
                return redirect("/store")
            else:
                login_error = "Неправильний email або пароль"

    return render(
        request,
        "auth_page/auth.html",
        {
            "form": form,
            "login_error": login_error,
        },
    )

def logout_view(request):
    logout(request)
    return redirect("/")