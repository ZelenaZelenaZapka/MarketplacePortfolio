import re
from django import forms
from django.contrib.auth.models import User
from .models import Product
from django.utils.text import slugify

class RegisterUserForm(forms.Form):
    ROLE_CHOICES = (
        ("buyer", "Покупець"),
        ("seller", "Продавець"),
    )

    name = forms.CharField(
        max_length=100,
        error_messages={
            "required": "Введіть ім’я",
            "invalid": "Введіть коректний email",
        }
    )

    email = forms.EmailField(
        error_messages={
            "required": "Введіть email",
            "invalid": "Введіть коректний email",
        }
    )

    phone = forms.CharField(
        max_length=20,
        error_messages={
            "required": "Введіть номер телефону",
        }
    )

    password = forms.CharField(
        widget=forms.PasswordInput,
        min_length=8,
        error_messages={
            "required": "Введіть пароль",
            "min_length": "Пароль має містити мінімум 8 символів",
        }
    )

    confirm_password = forms.CharField(
        widget=forms.PasswordInput,
        min_length=8,
        error_messages={
            "required": "Підтвердіть пароль",
            "min_length": "Підтвердження пароля має містити мінімум 8 символів",
        }
    )

    role = forms.ChoiceField(
        choices=ROLE_CHOICES,
        error_messages={
            "required": "Оберіть роль",
            "invalid_choice": "Оберіть коректну роль",
        }
    )

    def clean_email(self):
        email = self.cleaned_data.get("email")

        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Користувач з таким email вже існує")

        return email

    def clean_phone(self):
        phone = self.cleaned_data.get("phone", "").strip()

        if not re.fullmatch(r"^\+?\d{10,15}$", phone):
            raise forms.ValidationError("Введіть коректний номер телефону")

        return phone

    def clean(self):
        cleaned_data = super().clean()

        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Паролі не співпадають")

        return cleaned_data
    

class StoreForm(forms.Form):
    name = forms.CharField(
        max_length=400,
        error_messages={
            "required": "Введіть назву магазину",
        }
    )

    description = forms.CharField(
        required=False,
        widget=forms.Textarea,
    )

    def clean_name(self):
        name = self.cleaned_data.get("name", "").strip()

        if not name:
            raise forms.ValidationError("Введіть назву магазину")

        return name    


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'description', 'image', 'price', 'category']
