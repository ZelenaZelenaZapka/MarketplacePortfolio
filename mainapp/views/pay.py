import uuid
import hashlib
from django.shortcuts import render
from django.http import JsonResponse
from django.db import transaction
from django.utils import timezone
from datetime import timedelta
from .order import get_cart_data
from ..models import Order, OrderItem, Payment, Product, Customer, Cart


def pay_render(request):
    data_context = get_cart_data(request)
    
    DELIVERY_PRICES = {
        'courier': 99.00,
        'pickup': 0.00,
    }

    if request.method == 'POST':
        post_data = request.POST
        
        delivery_type = post_data.get('delivery', 'courier')
        delivery_cost = DELIVERY_PRICES.get(delivery_type, 99.00)
        final_amount = data_context['total_price'] + delivery_cost

        with transaction.atomic():
            current_customer = None
            guest_info = ""

            if request.user.is_authenticated:
                try:
                    current_customer = request.user.customer
                    guest_info = f"Auth User: {request.user.email}"
                except Customer.DoesNotExist:
                    guest_info = f"Auth User (no profile): {request.user.email}"
            else:
                guest_info = (
                    f"ГІСТЬ: {post_data.get('firstName')} {post_data.get('lastName')}\n"
                    f"Тел: {post_data.get('phone')}\n"
                    f"Email: {post_data.get('email')}"
                )

            if delivery_type == 'pickup':
                final_delivery_str = f"Pickup from the point ID: {post_data.get('store_id')}"
            else:
                final_delivery_str = f"Courier: {post_data.get('address')}"

            order = Order.objects.create(
                customer=current_customer,
                amount=final_amount,
                delivery=final_delivery_str,
                customer_info=guest_info,
                status='pending'
            )

            for item in data_context['cart_items']:
                product_obj = Product.objects.get(id=item['id'])
                OrderItem.objects.create(
                    order=order,
                    product=product_obj,
                    quantity=item['quantity'],
                    price=item['price'],
                )

            Payment.objects.create(
                order=order,
                amount=final_amount,
                provider='card' if post_data.get('payment') == 'card' else 'cash',
                transaction_id=str(uuid.uuid4()),
                status='pending'
            )

            if request.user.is_authenticated:
                Cart.objects.filter(customer__user=request.user).delete()
            else:
                if 'cart' in request.session:
                    del request.session['cart']
                request.session.modified = True

            # === SECURE: save data about verification of owner ===
            if request.user.is_authenticated:
                request.session['last_order_id'] = order.id
            else:
                # For guset generated sercet token
                # And from email and timeset make hash
                guest_email = post_data.get('email', '')
                secret_string = f"{order.id}:{guest_email}:{timezone.now().timestamp()}"
                guest_token = hashlib.sha256(secret_string.encode()).hexdigest()
                
                request.session['last_order_id'] = order.id
                request.session['last_order_token'] = guest_token
            
            request.session.modified = True
            request.session.save()

            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'redirect_url': f'/thanks/{order.id}/'
                })

    return render(request, "pay_page/main_pay.html", context=data_context)

def thanks_page(request, order_id):
    try:
        order = Order.objects.select_related('customer__user').get(id=order_id)
        
        # Order no older than 30 minutes 
        if order.created_at < timezone.now() - timedelta(minutes=30):
            return render(request, "pay_page/thanks.html", {
                'error': 'Замовлення застаріло або не знайдено',
                'total_price': None,
                'order_id': None,
                'order': None,
            })
        
        user_has_access = False
        
        # Who can see order
        if request.user.is_authenticated:
            if order.customer and order.customer.user == request.user:
                user_has_access = True
                print(f"✅ Auth user {request.user.email} has access to order {order_id}")
            else:
                print(f"❌ Auth user {request.user.email} tried to access order {order_id} (not theirs)")
        else:
            session_token = request.session.get('last_order_token')
            session_order_id = request.session.get('last_order_id')
            
            if session_order_id == order_id and session_token:
                user_has_access = True
                print(f"✅ Guest with token has access to order {order_id}")
            else:
                print(f"❌ Guest without valid token tried to access order {order_id}")
        
        if not user_has_access:
            return render(request, "pay_page/thanks.html", {
                'error': "You don't hace acces to this order",
                'total_price': None,
                'order_id': None,
                'order': None,
            })
        
        context = {
            'total_price': float(order.amount),
            'order_id': order.id,
            'order': order,
            'error': None,
        }
        
        # Clear session
        if 'last_order_id' in request.session:
            del request.session['last_order_id']
        if 'last_order_token' in request.session:
            del request.session['last_order_token']
        request.session.modified = True
        
        return render(request, "pay_page/thanks.html", context)
        
    except Order.DoesNotExist:
        return render(request, "pay_page/thanks.html", {
            'error': 'Order not found',
            'total_price': None,
            'order_id': None,
            'order': None,
        })