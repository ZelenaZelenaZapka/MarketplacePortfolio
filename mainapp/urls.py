from django.urls import path

from .views import auth, store, dashboard, order

urlpatterns = [
    path("/", auth.logout_view, name="logut"),
    path("store", store.store_page, name="store"),
    path("", auth.register_view, name="reg"),
    path("dashboard", dashboard.dashboard, name="dashboard"),
    path("dashboard/item", dashboard.item, name="item_dashboard"),
    path("dashboard/item/<int:product_id>/delete", dashboard.delete_product, name="delete_product"),
    path("dashboard/item/<int:product_id>/edit_product", dashboard.edit_product, name="edit_product"),
    path("cart/add/<int:product_id>/", order.add_to_cart, name="add_to_cart"),
    path("cart/", order.cart_detail, name="cart_detail"),
    path("cart/data", order.cart_data, name="cart_data"),
    path("cart/remove/<int:product_id>/", order.remove_from_cart, name="remove_from_cart"),
]

