from django.urls import path

from . import views

urlpatterns = [
    path("store", views.index, name="index"),
    path("", views.reg_page, name="reg"),
]
