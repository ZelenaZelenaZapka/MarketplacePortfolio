import uuid
from django.shortcuts import render
from django.http import JsonResponse
from django.db import transaction
from .order import get_cart_data
from ..models import Order, OrderItem, Payment, Product, Customer

def thanks_page(request):
    return render(request, "pay_page/thanks.html")

def pay_render(request):
    data_context = get_cart_data(request)
    
    if request.method == 'POST':
        post_data = request.POST
        
        # Використовуємо atomic, щоб якщо щось впаде, замовлення не створилося наполовину
        with transaction.atomic():
            # 1. Визначаємо хто купує
            current_customer = None
            guest_info = ""

            if request.user.is_authenticated:
                try:
                    current_customer = request.user.customer
                    guest_info = f"Auth User: {request.user.email}"
                except Customer.DoesNotExist:
                    # На випадок якщо у юзера чомусь нема профілю Customer
                    guest_info = f"Auth User (no profile): {request.user.email}"
            else:
                # Збираємо дані гостя в один текст
                guest_info = (
                    f"ГІСТЬ: {post_data.get('firstName')} {post_data.get('lastName')}\n"
                    f"Тел: {post_data.get('phone')}\n"
                    f"Email: {post_data.get('email')}"
                )

            # 2. Логіка доставки
            delivery_type = post_data.get('delivery')
            if delivery_type == 'pickup':
                # Можеш витягнути назву магазину з бази за ID, якщо треба
                final_delivery_str = f"Самовивіз з точки ID: {post_data.get('store_id')}"
            else:
                final_delivery_str = f"Кур'єр: {post_data.get('address')}"

            # 3. Створюємо Order
            order = Order.objects.create(
                customer=current_customer,
                amount=data_context['total_price'],
                delivery=final_delivery_str,
                customer_info=guest_info,
                status='pending'
            )

            # 4. Створюємо OrderItem для кожного товару з кошика
            for item in data_context['cart_items']:
                product_obj = Product.objects.get(id=item['id'])
                OrderItem.objects.create(
                    order=order,
                    product=product_obj,
                    quantity=item['quantity'],
                    price=item['price'],
                )

            # 5. Створюємо запис Payment
            Payment.objects.create(
                order=order,
                amount=data_context['total_price'],
                provider='card' if post_data.get('payment') == 'card' else 'cash',
                transaction_id=str(uuid.uuid4()), # Генеримо тимчасовий ID транзакції
                status='pending'
            )

            # 6. Очищуємо кошик (залежно від того, як він у тебе реалізований)
            # if not request.user.is_authenticated:
            #     if 'cart' in request.session:
            #         request.session['cart'] = {}
            # else:
            #     # Якщо в тебе кошик в БД для залогінених (моделі Cart/CartItem)
            #     data_context['cart'].items.all().delete()

            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'redirect_url': '/thanks/' # Створи цей URL або зміни на існуючий
                })

    return render(request, "pay_page/main_pay.html", context=data_context)