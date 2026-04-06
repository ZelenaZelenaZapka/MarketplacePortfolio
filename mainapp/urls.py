from django.urls import path

from .views import auth, store, dashboard

urlpatterns = [
    path("/", auth.logout_view, name="logut"),
    path("store", store.store_page, name="store"),
    path("", auth.register_view, name="reg"),
    path("dashboard", dashboard.dashboard, name="dashboard"),
    path("dashboard/item", dashboard.item, name="item_dashboard"),
]
    

