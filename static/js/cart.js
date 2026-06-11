/* ═══════════════════════════════════════
   Флорелла Кафе — Саватча логикаси
═══════════════════════════════════════ */
const cart = [];
const MIN_ORDER = 60000;

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
    const blocked = cart.length === 0 || total < MIN_ORDER;
    els.checkout.disabled = blocked;
    els.checkout.style.opacity = blocked ? '0.4' : '1';
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

  /* ── Minimal zakaz banneri (faqat dostavka) ── */
  const banner = document.getElementById('minOrderBanner');
  if (banner && cart.length > 0) {
    const remain = MIN_ORDER - total;
    if (remain > 0) {
      const pct = Math.min(100, Math.round((total / MIN_ORDER) * 100));
      banner.style.display = '';
      banner.innerHTML = `
        <div style="background:#fff0f1;border-radius:14px;padding:10px 12px;">
          <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px;">
            <span style="font-size:12px;font-weight:600;color:#5c5b5b;">Dostavka uchun yetishmaydi</span>
            <span style="font-size:12px;font-weight:800;color:#e31e24;">${fmt(remain)}</span>
          </div>
          <div style="height:6px;background:#f5c8c9;border-radius:999px;overflow:hidden;">
            <div style="height:100%;width:${pct}%;background:#e31e24;border-radius:999px;transition:width .3s;"></div>
          </div>
        </div>`;
    } else {
      banner.style.display = '';
      banner.innerHTML = `
        <div style="background:#e8f9ee;border-radius:14px;padding:10px 12px;
                    display:flex;align-items:center;gap:8px;">
          <span class="material-symbols-outlined" style="font-size:18px;color:#27ae60;font-variation-settings:'FILL' 1;">check_circle</span>
          <span style="font-size:12px;font-weight:700;color:#1a6b3a;">Minimal zakaz bajarildi ✓</span>
        </div>`;
    }
  } else if (banner) {
    banner.style.display = 'none';
  }

  /* ── Upsell tavsiyalar ── */
  _updateUpsell();

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

/* ── Upsell logikasi ── */
function _updateUpsell() {
  const sec    = document.getElementById('cartUpsell');
  const title  = document.getElementById('cartUpsellTitle');
  const wrap   = document.getElementById('cartUpsellItems');
  const all    = window._MENU_ITEMS || [];
  if (!sec || !wrap || cart.length === 0 || all.length === 0) {
    if (sec) sec.style.display = 'none';
    return;
  }

  const cartIds  = new Set(cart.map(i => i.id));
  const cartCats = new Set(cart.map(i => i.category));

  const PRIORITY = ['ichimliklar', 'zakuskalar', 'kokteyl', 'setlar', 'rolllar', 'pizzalar'];
  const missingCat = PRIORITY.find(c => !cartCats.has(c));

  let pool, label;
  if (missingCat) {
    pool  = all.filter(i => i.category === missingCat && !cartIds.has(i.id));
    const labels = {
      ichimliklar: '🥤 Ichimlik qo\'shing',
      zakuskalar:  '🥢 Zakuska qo\'shing',
      kokteyl:     '🍹 Kokteyl qo\'shing',
      setlar:      '🎁 Set qo\'shing',
      rolllar:     '🍱 Roll qo\'shing',
      pizzalar:    '🍕 Pizza qo\'shing',
    };
    label = labels[missingCat] || 'Qo\'shib ko\'ring';
  } else {
    pool  = all.filter(i => !cartIds.has(i.id));
    label = '⭐ Ko\'p sotilganlar';
  }

  const picks = pool.slice(0, 6);
  if (picks.length === 0) { sec.style.display = 'none'; return; }

  title.textContent = label;
  wrap.innerHTML = picks.map(item => {
    const imgHtml = item.image
      ? `<img src="/media/${item.image}" alt="" style="width:100%;height:100%;object-fit:cover;border-radius:10px;">`
      : `<span style="font-size:1.6rem;">${EMOJI[item.category] || '🍽️'}</span>`;
    return `
      <div style="flex:none;width:110px;background:#fff;border-radius:14px;
                  box-shadow:0 2px 8px rgba(0,0,0,.07);overflow:hidden;">
        <div style="height:72px;background:#f3f3f8;display:flex;align-items:center;
                    justify-content:center;overflow:hidden;">
          ${imgHtml}
        </div>
        <div style="padding:6px 8px 8px;">
          <p style="font-size:11px;font-weight:700;color:#1a1c1f;line-height:1.3;
                    overflow:hidden;display:-webkit-box;-webkit-line-clamp:2;
                    -webkit-box-orient:vertical;margin-bottom:4px;">${item.name}</p>
          <div style="display:flex;align-items:center;justify-content:space-between;">
            <span style="font-size:10px;font-weight:800;color:#ba0013;">${fmt(item.price)}</span>
            <button style="width:22px;height:22px;border-radius:6px;background:#e31e24;
                           border:none;cursor:pointer;display:flex;align-items:center;
                           justify-content:center;flex-shrink:0;"
                    onclick="_upsellAdd(${item.id})">
              <span class="material-symbols-outlined" style="font-size:14px;color:#fff;">add</span>
            </button>
          </div>
        </div>
      </div>`;
  }).join('');

  sec.style.display = '';
}

function _upsellAdd(id) {
  const all  = window._MENU_ITEMS || [];
  const item = all.find(i => i.id === id);
  if (!item) return;
  const ex = cart.find(i => i.id === id);
  if (ex) { ex.quantity++; }
  else {
    cart.push({ id: item.id, name: item.name, price: item.price,
                quantity: 1, image: item.image || '', category: item.category });
  }
  updateCartUI();
  if (typeof updateItemBadges === 'function') updateItemBadges();
}

updateCartUI();
