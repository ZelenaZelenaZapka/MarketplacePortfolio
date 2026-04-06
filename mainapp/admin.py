from django.contrib import admin
from .models import Customer, Product, Seller, CartItem, Category, OrderItem, Store, Order, Payment, Cart


admin.site.register(Customer)
admin.site.register(Seller)
admin.site.register(Category)
admin.site.register(Store)
admin.site.register(Product)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(Payment)