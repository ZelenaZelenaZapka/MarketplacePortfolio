// ===== УТИЛІТА: отримання CSRF токена =====
function getCookie(name) {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) return parts.pop().split(';').shift();
}

// ===== ГОЛОВНИЙ КОД =====
document.addEventListener('DOMContentLoaded', function() {
    
    // === 1. Елементи ===
    const deliveryRadios = document.querySelectorAll('input[name="delivery"]');
    const paymentRadios = document.querySelectorAll('input[name="payment"]');
    const addressField = document.getElementById('delivery-address-field');
    const pickupField = document.getElementById('pickup-store-field');
    const cardWrapper = document.getElementById('card-form-wrapper');
    
    // Елементи цін
    const btnTotal = document.getElementById('button-total-price');
    const deliveryPriceDisplay = document.getElementById('delivery-price-display');
    const cartGrandTotal = document.getElementById('cart-grand-total');
    
    // Базова ціна товарів (з Django)
    const baseTotal = parseFloat(document.body.dataset.baseTotal) || 0;
    
    // === 2. Логіка доставки ===
    function handleDeliveryChange() {
        const selected = document.querySelector('input[name="delivery"]:checked').value;
        
        // Показуємо/ховаємо поля
        if (selected === 'pickup') {
            addressField.style.display = 'none';
            addressField.querySelector('input').required = false;
            pickupField.style.display = 'block';
            pickupField.querySelector('select').required = true;
        } else {
            addressField.style.display = 'block';
            addressField.querySelector('input').required = true;
            pickupField.style.display = 'none';
            pickupField.querySelector('select').required = false;
        }
        
        // Оновлюємо ціни
        updatePrices(selected);
    }

    // === 3. Оновлення цін (ЛОКАЛЬНО, без AJAX — швидко і надійно) ===
    function updatePrices(deliveryType) {
        const deliveryCost = deliveryType === 'courier' ? 99 : 0;
        const newTotal = baseTotal + deliveryCost;
        
        // Форматуємо: 250 -> "250.00"
        const formattedDelivery = deliveryCost.toFixed(2);
        const formattedTotal = newTotal.toFixed(2);
        
        // Оновлюємо ВСІ місця де є ціна
        if (deliveryPriceDisplay) deliveryPriceDisplay.textContent = formattedDelivery;
        if (cartGrandTotal) cartGrandTotal.textContent = formattedTotal;
        if (btnTotal) btnTotal.textContent = `₴ ${formattedTotal}`;
    }

    // === 4. Логіка оплати ===
    function handlePaymentChange() {
        const selected = document.querySelector('input[name="payment"]:checked').value;
        
        if (selected === 'card') {
            cardWrapper.style.display = 'block';
            cardWrapper.querySelectorAll('input').forEach(input => input.required = true);
        } else {
            cardWrapper.style.display = 'none';
            cardWrapper.querySelectorAll('input').forEach(input => input.required = false);
        }
    }

    // === 5. Вішаємо події ===
    deliveryRadios.forEach(radio => {
        radio.addEventListener('change', handleDeliveryChange);
    });
    
    paymentRadios.forEach(radio => {
        radio.addEventListener('change', handlePaymentChange);
    });

    // === 6. Запускаємо при завантаженні ===
    handleDeliveryChange();
    handlePaymentChange();
    
    // === 7. AJAX відправка форми ===
    const form = document.getElementById('main-checkout-form');
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const formData = new FormData(form);
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

        try {
            const response = await fetch(window.location.href, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrfToken,
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: formData
            });

            const result = await response.json();
            
            if (result.success) {
                window.location.href = result.redirect_url;
            } else {
                alert(result.error || 'Сталася помилка при оформленні');
            }
        } catch (err) {
            console.error('Fetch error:', err);
            alert('Помилка зʼєднання з сервером');
        }
    });
});

// ===== КНОПКИ КІЛЬКОСТІ ТОВАРУ (окремий блок) =====
document.addEventListener('click', async (e) => {
  const btn = e.target.closest('.js-qty');
  if (!btn) return;

  const productId = btn.dataset.productId;
  const action = btn.dataset.action;

  const res = await fetch(`/cart/qty/${productId}/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': getCookie('csrftoken')
    },
    body: JSON.stringify({ action })
  });

  const data = await res.json();

  if (data.quantity === 0) {
      const item = document.querySelector(`[data-product-id="${productId}"]`);
      if (item) item.remove();
  } else {
      document.querySelector(`[data-qty-for="${productId}"]`).value = data.quantity;
      document.querySelector(`[data-item-total-for="${productId}"]`).textContent = data.item_total;
  }

  // Оновлюємо загальні ціни після зміни кількості
  document.getElementById('cart-goods-total').textContent = data.total_price;
  document.getElementById('cart-grand-total').textContent = data.total_price;
  document.getElementById('button-total-price').textContent = `₴ ${parseFloat(data.total_price).toFixed(2)}`;
});

// ===== КНОПКА ВИДАЛЕННЯ ТОВАРУ (окремий блок) =====
document.addEventListener('click', async (e) => {
  const btn = e.target.closest('.js-remove');
  if (!btn) return;

  const url = btn.dataset.url;
  const csrfToken = getCookie('csrftoken');

  try {
    const res = await fetch(url, {
      method: 'POST',
      headers: {
        'X-CSRFToken': csrfToken,
        'X-Requested-With': 'XMLHttpRequest',
      }
    });

    const data = await res.json();
    if (data.success) {
      location.reload();
    } else {
      alert(data.error || 'Не вдалося видалити товар');
    }
  } catch (err) {
    console.error(err);
    alert('Помилка мережі при видаленні');
  }
});