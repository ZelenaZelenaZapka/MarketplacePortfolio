from django.urls import path

from . import views

urlpatterns = [
    path("store", views.store_page, name="store"),
    path("", views.register_view, name="reg"),
]

