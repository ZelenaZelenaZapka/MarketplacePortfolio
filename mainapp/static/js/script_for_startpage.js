// static/js/cart_logic.js

document.addEventListener('DOMContentLoaded', function () {
    // Конфігурація URL
    const cartDataUrl = window.MarketHub?.cartDataUrl || '/cart/data/';
    const removeUrlBase = window.MarketHub?.removeUrlBase || '/cart/remove/';

    // --- ДОПОМІЖНІ ФУНКЦІЇ ---

    function getCsrfToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]')?.value || '';
    }

    function updateOrderBtnVisibility() {
        const cartItems = document.querySelectorAll('#cart-list .cart-item');
        const btn = document.querySelector('.js-order-btn');
        if (!btn) return;
        
        if (cartItems.length > 0) {
            btn.removeAttribute('hidden');
            btn.style.display = 'block';
        } else {
            btn.setAttribute('hidden', 'true');
            btn.style.display = 'none';
        }
    }

    function renderCart(data) {
        const cartList = document.getElementById('cart-list');
        const cartCountText = document.querySelector('.cart-count-text');
        const cartTotalPrice = document.getElementById('cart-total-price');
        
        if (cartCountText) cartCountText.textContent = data.cart_count;
        if (cartTotalPrice) cartTotalPrice.textContent = data.total_price;
        if (!cartList) return;

        if (!data.cart_items || !data.cart_items.length) {
            cartList.innerHTML = `<p class="muted">Кошик порожній</p>`;
            updateOrderBtnVisibility();
            return;
        }

        let itemsHtml = data.cart_items.map(item => `
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

        cartList.innerHTML = itemsHtml;
        updateOrderBtnVisibility();
    }

    function loadCartData() {
        fetch(cartDataUrl, {
            method: 'GET',
            headers: { 'X-Requested-With': 'XMLHttpRequest' }
        })
        .then(res => res.json())
        .then(data => {
            if (data.success) renderCart(data);
        })
        .catch(err => console.error('Помилка завантаження кошика:', err));
    }

    // --- ОБРОБНИКИ ПОДІЙ (ДЕЛЕГУВАННЯ) ---

    // 1. Обробка кліків (Кнопки видалення та анімація кнопок "Додати")
    document.addEventListener('click', function (e) {
        // Видалення з кошика
        const removeBtn = e.target.closest('.remove-btn');
        if (removeBtn) {
            const productId = removeBtn.dataset.productId;
            fetch(`${removeUrlBase}${productId}/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCsrfToken(),
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(res => res.json())
            .then(data => {
                if (data.success) loadCartData();
            });
            return;
        }

        // Анімація кнопки "Додати в кошик" (якщо це просто кнопка в формі)
        const addBtn = e.target.closest('.add-to-cart');
        if (addBtn) {
            const originalText = addBtn.textContent;
            addBtn.textContent = "Додано";
            addBtn.disabled = true;
            setTimeout(() => {
                addBtn.textContent = originalText;
                addBtn.disabled = false;
            }, 900);
        }
    });

    // 2. Обробка відправки форми (Додавання в кошик через AJAX)
    document.addEventListener('submit', function (e) {
        const form = e.target.closest('.add-to-cart-form');
        if (!form) return;

        e.preventDefault();
        const url = form.action;
        const csrfToken = form.querySelector('[name=csrfmiddlewaretoken]')?.value || getCsrfToken();

        fetch(url, {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrfToken,
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(res => res.json())
        .then(data => {
            if (data.success) loadCartData();
            else alert(data.error || 'Помилка при додаванні');
        });
    });

    // 3. Обробка перемикання чіпсів (Фільтри)
    document.addEventListener('change', function (e) {
        const checkbox = e.target.closest('.chip input');
        if (!checkbox) return;

        const chip = checkbox.parentElement;
        if (checkbox.checked) {
            chip.classList.add('active');
        } else {
            chip.classList.remove('active');
        }
    });

    // 4. Оновлення стану чіпсів після роботи HTMX
    document.body.addEventListener('htmx:afterSwap', function() {
        document.querySelectorAll('.chip input').forEach(input => {
            if (input.checked) {
                input.parentElement.classList.add('active');
            } else {
                input.parentElement.classList.remove('active');
            }
        });
    });

    // Початкове завантаження
    loadCartData();
});