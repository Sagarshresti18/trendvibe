// Image fallback — uses inline SVG data URI, never makes a network request
const PLACEHOLDER = "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='400' height='400'%3E%3Crect width='400' height='400' fill='%23e5e7eb'/%3E%3Ctext x='50%25' y='50%25' dominant-baseline='middle' text-anchor='middle' font-family='sans-serif' font-size='18' fill='%239ca3af'%3ENo Image%3C/text%3E%3C/svg%3E";

document.querySelectorAll('img.product-img').forEach((img) => {
  img.addEventListener('error', function () {
    // Remove the listener first so a broken fallback can't re-trigger this
    this.removeEventListener('error', arguments.callee);
    this.src = PLACEHOLDER;
  });
});

// Get CSRF token
const csrfToken = document.querySelector("meta[name='csrf-token']")?.content;

// Dark Mode Toggle
const themeToggle = document.getElementById('theme-toggle');
const currentTheme = localStorage.getItem('theme') || 'light';
document.documentElement.setAttribute('data-theme', currentTheme);

themeToggle?.addEventListener('click', () => {
const theme = document.documentElement.getAttribute('data-theme');
const newTheme = theme === 'light' ? 'dark' : 'light';
document.documentElement.setAttribute('data-theme', newTheme);
localStorage.setItem('theme', newTheme);
});

// Utility function for POST requests
const postJson = async (url, payload) => {
const response = await fetch(url, {
method: 'POST',
headers: { 'Content-Type': 'application/json' },
body: JSON.stringify(payload),
});
return response.json();
};

// Update cart count
const updateCartCount = (count) => {
const badge = document.getElementById('cart-count');
if (badge) {
badge.textContent = count;
badge.style.animation = 'none';
setTimeout(() => {
badge.style.animation = 'pulse 0.5s ease';
}, 10);
}
};

// Add to cart
document.body.addEventListener('click', async (e) => {
const btn = e.target.closest('[data-add-to-cart]');
if (!btn) return;
const productId = btn.dataset.addToCart;
const quantityInput = document.getElementById('quantity');
const quantity = quantityInput ? parseInt(quantityInput.value) : 1;
btn.disabled = true;
const originalText = btn.textContent;
btn.textContent = 'Adding...';
try {
const data = await postJson('/cart/add', {
product_id: productId,
quantity: quantity,
csrf_token: csrfToken,
});
if (data.error) {
alert(data.error);
return;
}
updateCartCount(data.cart_count);
btn.textContent = 'Added!';
setTimeout(() => {
btn.textContent = originalText;
btn.disabled = false;
}, 1500);
} catch (error) {
console.error('Error:', error);
alert('Failed to add item to cart');
btn.textContent = originalText;
btn.disabled = false;
}
});

// Update cart
document.body.addEventListener('click', async (e) => {
const btn = e.target.closest('[data-cart-update]');
if (!btn) return;
const productId = btn.dataset.cartUpdate;
const quantity = Number(btn.dataset.quantity);
try {
const data = await postJson('/cart/update', {
product_id: productId,
quantity: quantity,
csrf_token: csrfToken,
});
if (data.error) {
alert(data.error);
return;
}
window.location.reload();
} catch (error) {
console.error('Error:', error);
alert('Failed to update cart');
}
});

// Wishlist toggle
document.body.addEventListener('click', async (e) => {
const btn = e.target.closest('[data-wishlist-toggle]');
if (!btn) return;
e.preventDefault();
e.stopPropagation();
const productId = btn.dataset.wishlistToggle;
const isActive = btn.classList.contains('active');
const endpoint = isActive ? '/wishlist/remove' : '/wishlist/add';
try {
const data = await postJson(endpoint, {
product_id: productId,
csrf_token: csrfToken,
});
if (data.error) {
if (data.error === 'Please log in') {
window.location.href = '/login';
return;
}
alert(data.error);
return;
}
btn.classList.toggle('active');
const svg = btn.querySelector('svg path');
if (svg) {
svg.setAttribute('fill', isActive ? 'none' : 'currentColor');
}
if (window.location.pathname.includes('profile') && isActive) {
const card = btn.closest('.product-card');
if (card) {
card.style.opacity = '0';
setTimeout(() => card.remove(), 300);
}
}
} catch (error) {
console.error('Error:', error);
alert('Failed to update wishlist');
}
});

// Quantity selectors
document.querySelectorAll('.quantity-selector').forEach((selector) => {
const input = selector.querySelector('.qty-input');
const decreaseBtn = selector.querySelector('[data-action="decrease"]');
const increaseBtn = selector.querySelector('[data-action="increase"]');
if (decreaseBtn) {
decreaseBtn.addEventListener('click', () => {
const currentValue = parseInt(input.value);
const minValue = parseInt(input.min) || 1;
if (currentValue > minValue) {
input.value = currentValue - 1;
}
});
}
if (increaseBtn) {
increaseBtn.addEventListener('click', () => {
const currentValue = parseInt(input.value);
const maxValue = parseInt(input.max) || 999;
if (currentValue < maxValue) {
input.value = currentValue + 1;
}
});
}
});

// Profile tabs
document.querySelectorAll('.tab-btn').forEach((btn) => {
btn.addEventListener('click', () => {
const targetTab = btn.dataset.tab;
document.querySelectorAll('.tab-btn').forEach((b) => b.classList.remove('active'));
document.querySelectorAll('.tab-content').forEach((c) => c.classList.remove('active'));
btn.classList.add('active');
const targetContent = document.getElementById(targetTab);
if (targetContent) {
targetContent.classList.add('active');
}
});
});

// ── Cancel Order ────────────────────────────────────────────────
const cancelModal   = document.getElementById('cancel-modal');
const modalOrderRef = document.getElementById('modal-order-ref');
const modalConfirm  = document.getElementById('modal-confirm');
const modalDismiss  = document.getElementById('modal-dismiss');
let pendingCancelId  = null;
let pendingCancelBtn = null;

document.body.addEventListener('click', (e) => {
  const btn = e.target.closest('[data-cancel-order]');
  if (!btn) return;
  pendingCancelId  = btn.dataset.cancelOrder;
  pendingCancelBtn = btn;
  if (modalOrderRef) modalOrderRef.textContent = btn.dataset.orderRef || 'this order';
  if (cancelModal)   cancelModal.hidden = false;
});

modalDismiss?.addEventListener('click', () => {
  cancelModal.hidden = true;
  pendingCancelId = null;
  pendingCancelBtn = null;
});

cancelModal?.addEventListener('click', (e) => {
  if (e.target === cancelModal) {
    cancelModal.hidden = true;
    pendingCancelId = null;
    pendingCancelBtn = null;
  }
});

modalConfirm?.addEventListener('click', async () => {
  if (!pendingCancelId) return;
  modalConfirm.disabled = true;
  modalConfirm.textContent = 'Cancelling…';

  try {
    const data = await postJson(`/order/cancel/${pendingCancelId}`, {
      csrf_token: csrfToken,
    });

    cancelModal.hidden = true;

    if (data.error) {
      alert(data.error);
    } else {
      // Update the status badge in the card without a full reload
      const card = pendingCancelBtn.closest('.order-card');
      if (card) {
        const badge = card.querySelector('.order-status');
        if (badge) {
          badge.textContent = 'Cancelled';
          badge.className = 'order-status status-cancelled';
        }
        // Remove the cancel button — can't cancel twice
        pendingCancelBtn.remove();
      }
    }
  } catch (err) {
    alert('Something went wrong. Please try again.');
  } finally {
    modalConfirm.disabled = false;
    modalConfirm.textContent = 'Yes, Cancel Order';
    pendingCancelId  = null;
    pendingCancelBtn = null;
  }
});

// Auto-hide flash messages
setTimeout(() => {
document.querySelectorAll('.flash').forEach((flash) => {
flash.style.opacity = '0';
flash.style.transform = 'translateX(100%)';
setTimeout(() => flash.remove(), 300);
});
}, 5000);

// Add pulse animation
const style = document.createElement('style');
style.textContent = `
@keyframes pulse {
0%, 100% { transform: scale(1); }
50% { transform: scale(1.2); }
}
`;
document.head.appendChild(style);
