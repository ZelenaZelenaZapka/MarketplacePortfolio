from django.urls import path

from .views import auth, store, dashboard, order, pay, card_render

urlpatterns = [
    path("store", store.store_page, name="store"),
    path("", auth.register_view, name="reg"),
    path("dashboard/", dashboard.seller_dashboard, name="dashboard"),
    path("dashboard/product/<int:product_id>/", dashboard.seller_dashboard, name="dashboard_product"),
    path("cart/add/<int:product_id>/", order.add_to_cart, name="add_to_cart"),
    path("cart/", order.cart_detail, name="cart_detail"),
    path("cart/data", order.cart_data, name="cart_data"),
    path("cart/remove/<int:product_id>/", order.remove_from_cart, name="remove_from_cart"),
    path("pay/", pay.pay_render, name="pay_render"),
    path("cart/qty/<int:product_id>/", order.change_quantity, name="change_quantity"),
    path("thanks/<int:order_id>/", pay.thanks_page, name="thanks"),
    path("item_page/<int:item_id>/", card_render.cart_product_render, name="card_product"),
    path("", store.logout_view, name="logout"),
]


