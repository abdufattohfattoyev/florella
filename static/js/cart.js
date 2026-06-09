/* ═══════════════════════════════════════
   Флорелла Кафе — Саватча логикаси
═══════════════════════════════════════ */
const cart = [];

const fmt = n =>
  new Intl.NumberFormat('uz-UZ').format(Math.round(n)) + ' сўм';

const EMOJI = {
  rolllar:'🍱', pizzalar:'🍕', setlar:'🎁',
  zakuskalar:'🥢', ichimliklar:'🍵', kokteyl:'🍹'
};

function _cartItemThumb(item) {
  if (item.image) {
    return `<img src="${item.image}" alt=""
              style="width:100%;height:100%;object-fit:cover;border-radius:12px;">`;
  }
  return `<span style="font-size:1.6rem;">${EMOJI[item.category] || '🍽️'}</span>`;
}

function updateCartUI() {
  const els = {
    items:    document.getElementById('cartItems'),
    total:    document.getElementById('cartTotal'),
    countBot: document.getElementById('cartCountBottom'),
    checkout: document.getElementById('checkoutBtn'),
    dataIn:   document.getElementById('cartDataInput'),
    summary:  document.getElementById('modalOrderSummary'),
  };

  const count = cart.reduce((s, i) => s + i.quantity, 0);
  const total = cart.reduce((s, i) => s + i.price * i.quantity, 0);

  if (els.countBot) els.countBot.textContent = count;
  if (els.total)    els.total.textContent = fmt(total);
  if (els.checkout) {
    els.checkout.disabled = cart.length === 0;
    els.checkout.style.opacity = cart.length === 0 ? '0.4' : '1';
  }
  if (els.dataIn) els.dataIn.value = JSON.stringify(cart);

  /* ── Cart item list ── */
  if (els.items) {
    if (cart.length === 0) {
      els.items.innerHTML = `
        <div style="display:flex;flex-direction:column;align-items:center;justify-content:center;
                    padding:52px 20px;gap:10px;text-align:center;">
          <span style="font-size:3rem;">🛒</span>
          <p style="font-weight:700;font-size:.9rem;color:#1a1c1f;">Саватча бўш</p>
          <p style="font-size:.78rem;color:#5c5b5b;">Таом танлаб қўшинг</p>
        </div>`;
    } else {
      els.items.innerHTML = cart.map(item => `
        <div style="display:flex;align-items:center;gap:12px;padding:12px 0;
                    border-bottom:1px solid rgba(231,189,184,.45);">
          <!-- Rasm -->
          <div style="width:52px;height:52px;border-radius:12px;
                      background:#f3f3f8;flex-shrink:0;overflow:hidden;
                      display:flex;align-items:center;justify-content:center;">
            ${_cartItemThumb(item)}
          </div>
          <!-- Info -->
          <div style="flex:1;min-width:0;">
            <p style="font-weight:700;font-size:.875rem;color:#1a1c1f;
                      overflow:hidden;text-overflow:ellipsis;white-space:nowrap;
                      margin-bottom:2px;">${item.name}</p>
            <p style="font-weight:800;font-size:.875rem;color:#ba0013;">
              ${fmt(item.price)}<span style="font-size:.72rem;font-weight:600;color:#5c5b5b;"> / dona</span>
            </p>
          </div>
          <!-- Qty controls -->
          <div style="display:flex;align-items:center;gap:0;
                      background:#f3f3f8;border-radius:12px;padding:4px;flex-shrink:0;">
            <button onclick="changeQty(${item.id},${item.price},-1)"
                    title="${item.quantity === 1 ? "O'chirish" : 'Kamaytirish'}"
                    style="width:30px;height:30px;border-radius:8px;border:none;
                           background:${item.quantity === 1 ? '#ffe4e4' : 'transparent'};
                           cursor:pointer;display:flex;align-items:center;justify-content:center;
                           color:${item.quantity === 1 ? '#e31e24' : '#1a1c1f'};">
              ${item.quantity === 1
                ? '<span class="material-symbols-outlined" style="font-size:16px;">delete</span>'
                : '<span style="font-size:1.2rem;font-weight:700;line-height:1;">−</span>'
              }
            </button>
            <span style="font-weight:800;font-size:.9rem;min-width:22px;text-align:center;color:#1a1c1f;">${item.quantity}</span>
            <button onclick="changeQty(${item.id},${item.price},1)"
                    style="width:30px;height:30px;border-radius:8px;background:#e31e24;border:none;
                           cursor:pointer;display:flex;align-items:center;justify-content:center;color:#fff;">
              <span class="material-symbols-outlined" style="font-size:16px;">add</span>
            </button>
          </div>
        </div>`).join('');
    }
  }

  /* ── Modal summary ── */
  if (els.summary) {
    els.summary.innerHTML = cart.length === 0
      ? `<p style="font-size:.8125rem;color:#5c5b5b;text-align:center;">Саватча бўш</p>`
      : cart.map(i => `
          <div style="display:flex;justify-content:space-between;align-items:center;
                      padding:5px 0;border-bottom:1px solid rgba(231,189,184,.4);">
            <span style="font-size:.8125rem;color:#5c5b5b;">${i.name} × ${i.quantity}</span>
            <span style="font-size:.8125rem;font-weight:700;color:#ba0013;">${fmt(i.price * i.quantity)}</span>
          </div>`).join('')
        + `<div style="display:flex;justify-content:space-between;align-items:center;padding-top:8px;">
             <span style="font-weight:600;font-size:.875rem;color:#1a1c1f;">Жами тўлов:</span>
             <span style="font-weight:800;font-size:1rem;color:#ba0013;">${fmt(total)}</span>
           </div>`;
  }
}

function changeQty(id, price, delta) {
  const idx = cart.findIndex(i => i.id === id && i.price === price);
  if (idx === -1) return;
  cart[idx].quantity += delta;
  if (cart[idx].quantity <= 0) cart.splice(idx, 1);
  updateCartUI();
  if (typeof updateItemBadges === 'function') updateItemBadges();
}

updateCartUI();
