function getCookie(name) {
      const value = `; ${document.cookie}`;
      const parts = value.split(`; ${name}=`);
      if (parts.length === 2) return parts.pop().split(';').shift();
    }

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

      function getCookie(name) {
      const v = `; ${document.cookie}`;
      const parts = v.split(`; ${name}=`);
      if (parts.length === 2) return parts.pop().split(';').shift();
    }

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

      // ... всередині обробника кліку js-qty ...

      const data = await res.json();

      if (data.quantity === 0) {
          const item = document.querySelector(`[data-product-id="${productId}"]`);
          if (item) item.remove();
      } else {
          document.querySelector(`[data-qty-for="${productId}"]`).value = data.quantity;
          document.querySelector(`[data-item-total-for="${productId}"]`).textContent = data.item_total;
      }

      // Оновлюємо загальну ціну в кошику (це у тебе вже було)
      document.getElementById('cart-goods-total').textContent = data.total_price;
      document.getElementById('cart-grand-total').textContent = data.total_price;

      // А ОСЬ ЦЕ ДОДАЄМО: оновлюємо ціну прямо в кнопці
      document.getElementById('button-total-price').textContent = `₴ ${data.total_price}`;
    });

document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('main-checkout-form');
    
    // Перемикачі
    const deliveryRadios = document.querySelectorAll('input[name="delivery"]');
    const paymentRadios = document.querySelectorAll('input[name="payment"]');
    
    // Блоки для приховування
    const addressField = document.getElementById('delivery-address-field');
    const storeField = document.getElementById('pickup-store-field');
    const cardWrapper = document.getElementById('card-form-wrapper');

    // Логіка доставки
    deliveryRadios.forEach(radio => {
        radio.addEventListener('change', (e) => {
            if (e.target.value === 'pickup') {
                addressField.style.display = 'none';
                addressField.querySelector('input').required = false;
                storeField.style.display = 'block';
            } else {
                addressField.style.display = 'block';
                addressField.querySelector('input').required = true;
                storeField.style.display = 'none';
            }
        });
    });

    // Логіка оплати
    paymentRadios.forEach(radio => {
        radio.addEventListener('change', (e) => {
            cardWrapper.style.display = (e.target.value === 'card') ? 'block' : 'none';
            // Опціонально: знімаємо required з полів карти, якщо вибрано готівку
            const cardInputs = cardWrapper.querySelectorAll('input');
            cardInputs.forEach(input => input.required = (e.target.value === 'card'));
        });
    });

    // AJAX відправка
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
                // Перенаправлення на сторінку успіху
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