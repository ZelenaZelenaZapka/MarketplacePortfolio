// 1. ГЛОБАЛЬНІ ФУНКЦІЇ

window.renderCart = function(data) {
    const cartList = document.getElementById('cart-list');
    const cartCountTexts = document.querySelectorAll('.cart-count-text');
    const cartTotalPrice = document.getElementById('cart-total-price');
    const orderBtn = document.querySelector('.js-order-btn'); // Наша кнопка

    // Оновлюємо цифру лічильника
    cartCountTexts.forEach(el => {
        el.textContent = data.cart_count || 0;
    });

    // Оновлюємо загальну ціну
    if (cartTotalPrice) {
        cartTotalPrice.textContent = (data.total_price || 0) + " ₴";
    }

    // ЛОГІКА КНОПКИ "ОФОРМИТИ ЗАМОВЛЕННЯ"
    if (orderBtn) {
        if (data.cart_items && data.cart_items.length > 0) {
            orderBtn.style.display = 'block'; // Показуємо
            orderBtn.removeAttribute('hidden');
            orderBtn.style.pointerEvents = 'auto';
            orderBtn.style.opacity = '1';
        } else {
            orderBtn.style.display = 'none'; // Ховаємо
            orderBtn.setAttribute('hidden', 'true');
        }
    }

    if (!cartList) return;

    // Якщо товарів немає
    if (!data.cart_items || data.cart_items.length === 0) {
        cartList.innerHTML = `<p class="muted" style="padding: 20px; text-align: center;">Кошик порожній</p>`;
        return;
    }

    // Рендеримо список товарів
    cartList.innerHTML = data.cart_items.map(item => `
        <div class="cart-item">
            <div class="cart-thumb">
                <img src="${item.image_url || '/static/img/product-placeholder.png'}" alt="${item.name}">
            </div>
            <div class="cart-info">
                <h4>${item.name}</h4>
                <p>${item.quantity} × ${item.price} ₴</p>
            </div>
            <div class="cart-side">
                <strong>${item.item_total} ₴</strong>
                <button class="remove-btn" type="button" data-product-id="${item.id}">×</button>
            </div>
        </div>
    `).join('');
};

window.loadCartData = function() {
    const cartDataUrl = window.MarketHub?.cartDataUrl || '/cart/data/';
    
    fetch(cartDataUrl, { 
        headers: { 'X-Requested-With': 'XMLHttpRequest' } 
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            window.renderCart(data);
        }
    })
    .catch(err => console.error("Помилка завантаження кошика:", err));
};

window.addToCart = function(button) {
    const form = button.closest('form');
    if (!form) return;

    const url = form.action;
    const csrfToken = form.querySelector('[name=csrfmiddlewaretoken]')?.value;

    fetch(url, {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrfToken,
            'X-Requested-With': 'XMLHttpRequest'
        },
        body: new FormData(form)
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            window.loadCartData(); // Це оновить і список, і кнопку
            
            const originalText = button.textContent;
            button.textContent = "Додано!";
            button.classList.add('btn-success'); 
            setTimeout(() => {
                button.textContent = originalText;
                button.classList.remove('btn-success');
            }, 800);
        } else {
            alert(data.error || "Помилка");
        }
    })
    .catch(err => console.error("Помилка:", err));
};

// 2. ПОДІЇ
document.addEventListener('DOMContentLoaded', function () {
    const removeUrlBase = window.MarketHub?.removeUrlBase || '/cart/remove/';

    document.addEventListener('click', function (e) {
        const removeBtn = e.target.closest('.remove-btn');
        if (removeBtn) {
            const productId = removeBtn.dataset.productId;
            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value;

            fetch(`${removeUrlBase}${productId}/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrfToken,
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(res => res.json())
            .then(data => {
                if (data.success) window.loadCartData();
            });
        }
    });

    document.body.addEventListener('htmx:afterSwap', function() {
        window.loadCartData();
    });

    window.loadCartData();
});