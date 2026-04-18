// static/js/cart_logic.js

document.addEventListener('DOMContentLoaded', function () {
  // 🔥 Ці змінні ми отримаємо з HTML через data-атрибути або window
  const cartDataUrl = window.MarketHub?.cartDataUrl || '/cart/data/';
  const removeUrlBase = window.MarketHub?.removeUrlBase || '/cart/remove/';

  const forms = document.querySelectorAll('.add-to-cart-form');
  const chips = document.querySelectorAll('.chip');
  const addToCartButtons = document.querySelectorAll('.add-to-cart');

  // ===== CHIP toggle =====
  chips.forEach(chip => {
    chip.addEventListener('click', () => {
      chip.classList.toggle('active');
    });
  });

  // ===== Add to cart animation =====
  addToCartButtons.forEach(button => {
    button.addEventListener('click', () => {
      const originalText = button.textContent;
      button.textContent = "Додано";
      button.disabled = true;
      setTimeout(() => {
        button.textContent = originalText;
        button.disabled = false;
      }, 900);
    });
  });

  // ===== CSRF helper =====
  function getCsrfToken() {
    const csrfInput = document.querySelector('[name=csrfmiddlewaretoken]');
    return csrfInput ? csrfInput.value : '';
  }

  // ===== Cart UI helpers =====
  function updateOrderBtnVisibility() {
    const cartItems = document.querySelectorAll('#cart-list .cart-item');
    const btn = document.querySelector('.js-order-btn');
    if (!btn) return;
    if (cartItems.length > 0) {
      btn.removeAttribute('hidden');
      btn.style.display = '';
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

    if (!data.cart_items.length) {
      cartList.innerHTML = `<p class="muted">Кошик порожній</p>`;
      updateOrderBtnVisibility();
      return;
    }

    let itemsHtml = '';
    data.cart_items.forEach(item => {
      const imageUrl = item.image_url || '/static/img/product-placeholder.png';
      itemsHtml += `
        <div class="cart-item">
          <div class="cart-thumb">
            <img src="${imageUrl}" alt="${item.name}">
          </div>
          <div class="cart-info">
            <h4>${item.name}</h4>
            <p>${item.quantity} × ${item.price} ₴</p>
          </div>
          <div class="cart-side">
            <strong>${item.item_total} ₴</strong>
            <button class="remove-btn" type="button" data-product-id="${item.id}">×</button>
          </div>
        </div>`;
    });
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
      else console.error('Не вдалося завантажити кошик');
    })
    .catch(err => console.error('Помилка завантаження кошика:', err));
  }

  // ===== Form submit (add to cart) =====
  document.addEventListener('submit', function (e) {
    // Перевіряємо, чи це форма додавання в кошик
    const form = e.target.closest('.add-to-cart-form');
    if (!form) return;

    e.preventDefault(); 
    const button = form.querySelector('.add-to-cart');
    const csrfToken = form.querySelector('[name=csrfmiddlewaretoken]')?.value || '';
    const url = form.action;

    if (button) {
      const originalText = button.textContent;
      button.textContent = "Додано";
      button.disabled = true;
      setTimeout(() => {
        button.textContent = originalText;
        button.disabled = false;
      }, 900);
    }

    fetch(url, {
      method: 'POST',
      headers: {
        'X-CSRFToken': csrfToken,
        'X-Requested-With': 'XMLHttpRequest'
      }
    })
    .then(res => res.json())
    .then(data => {
      if (data.success) {
        loadCartData(); // Оновлюємо кошик після успіху
      } else {
        console.error(data.error);
      }
    })
    .catch(err => console.error('Помилка:', err));
  });

  // ===== Remove from cart (delegate) =====
  document.addEventListener('click', function (event) {
    const removeButton = event.target.closest('.remove-btn');
    if (!removeButton) return;
    
    const productId = removeButton.dataset.productId;
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
      else console.error(data.error);
    })
    .catch(err => console.error('Помилка видалення:', err));
  });

  // ===== Init =====
  loadCartData();
});   

