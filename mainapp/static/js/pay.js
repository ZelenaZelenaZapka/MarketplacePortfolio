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
    
    // 🔧 Базова ціна товарів (з Django) - let, щоб можна було змінювати
    let baseTotal = parseFloat(document.body.dataset.baseTotal) || 0;
    
    // === 2. Логіка доставки ===
    function handleDeliveryChange() {
        const selected = document.querySelector('input[name="delivery"]:checked')?.value;
        if (!selected) return;
        
        // Показуємо/ховаємо поля адреси/самовивозу
        if (selected === 'pickup') {
            if (addressField) {
                addressField.style.display = 'none';
                const input = addressField.querySelector('input');
                if (input) input.required = false;
            }
            if (pickupField) {
                pickupField.style.display = 'block';
                const select = pickupField.querySelector('select');
                if (select) select.required = true;
            }
        } else {
            if (addressField) {
                addressField.style.display = 'block';
                const input = addressField.querySelector('input');
                if (input) input.required = true;
            }
            if (pickupField) {
                pickupField.style.display = 'none';
                const select = pickupField.querySelector('select');
                if (select) select.required = false;
            }
        }
        
        // Оновлюємо ціни з урахуванням доставки
        updatePrices(selected);
    }

    // === 3. Оновлення цін (ЛОКАЛЬНО, без AJAX) ===
    function updatePrices(deliveryType) {
        const deliveryCost = deliveryType === 'courier' ? 99 : 0;
        // 🔧 Використовуємо актуальне значення baseTotal з області видимості
        const newTotal = baseTotal + deliveryCost;
        
        // Форматуємо: 250 -> "250.00"
        const formattedDelivery = deliveryCost.toFixed(2);
        const formattedTotal = newTotal.toFixed(2);
        
        // Оновлюємо ВСІ місця, де відображається ціна
        if (deliveryPriceDisplay) deliveryPriceDisplay.textContent = formattedDelivery;
        if (cartGrandTotal) cartGrandTotal.textContent = formattedTotal;
        if (btnTotal) btnTotal.textContent = `₴ ${formattedTotal}`;
    }

    // === 4. Логіка оплати ===
    function handlePaymentChange() {
        const selected = document.querySelector('input[name="payment"]:checked')?.value;
        if (!selected) return;
        
        if (selected === 'card') {
            if (cardWrapper) {
                cardWrapper.style.display = 'block';
                cardWrapper.querySelectorAll('input').forEach(input => input.required = true);
            }
        } else {
            if (cardWrapper) {
                cardWrapper.style.display = 'none';
                cardWrapper.querySelectorAll('input').forEach(input => input.required = false);
            }
        }
    }

    // === 5. Вішаємо події на радіокнопки ===
    deliveryRadios.forEach(radio => {
        radio.addEventListener('change', handleDeliveryChange);
    });
    
    paymentRadios.forEach(radio => {
        radio.addEventListener('change', handlePaymentChange);
    });

    // === 6. Запускаємо при завантаженні ===
    handleDeliveryChange();
    handlePaymentChange();
    
    // === 7. AJAX відправка форми замовлення ===
    const form = document.getElementById('main-checkout-form');
    if (form) {
        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const formData = new FormData(form);
            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value;

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
    }

    // ===== 🔧 КНОПКИ КІЛЬКОСТІ ТОВАРУ (+/-) =====
    // Перенесено всередину DOMContentLoaded, щоб бачити updatePrices та baseTotal
    document.addEventListener('click', async (e) => {
      const btn = e.target.closest('.js-qty');
      if (!btn) return;

      const productId = btn.dataset.productId;
      const action = btn.dataset.action;

      try {
        const res = await fetch(`/cart/qty/${productId}/`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
          },
          body: JSON.stringify({ action })
        });

        if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);
        const data = await res.json();

        // 🛠️ Діагностичний лог (можна прибрати потім)
        // console.log('📦 Update response:', data);

        // 1. Оновлюємо UI товару
        if (data.quantity === 0) {
            // Якщо кількість 0 - видаляємо елемент зі списку
            const item = document.querySelector(`[data-product-id="${productId}"]`);
            if (item) item.remove();
        } else {
            // Оновлюємо інпут кількості
            const qtyInput = document.querySelector(`[data-qty-for="${productId}"]`);
            if (qtyInput) qtyInput.value = data.quantity;
            
            // Оновлюємо ціну за цей товар
            const itemTotalSpan = document.querySelector(`[data-item-total-for="${productId}"]`);
            if (itemTotalSpan && data.item_total) {
                itemTotalSpan.textContent = data.item_total;
            }
        }

        // 2. 🔥 ГОЛОВНЕ: Оновлюємо загальну суму
        // Перевіряємо, чи сервер повернув total_price
        if (data.total_price !== undefined && data.total_price !== null) {
            // Парсимо і оновлюємо локальну змінну baseTotal
            const parsedTotal = parseFloat(data.total_price);
            if (!isNaN(parsedTotal)) {
                baseTotal = parsedTotal;
                document.body.dataset.baseTotal = baseTotal;
                
                // Отримуємо поточний тип доставки і перераховуємо фінал
                const selectedDelivery = document.querySelector('input[name="delivery"]:checked')?.value || 'courier';
                updatePrices(selectedDelivery);
            }
        }
        
      } catch (err) {
        console.error('Qty update error:', err);
        // Не блокуємо користувача, якщо оновлення кількості впало
      }
    });

    // ===== 🔧 КНОПКА ВИДАЛЕННЯ ТОВАРУ =====
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

}); 


