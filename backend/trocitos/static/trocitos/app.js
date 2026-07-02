const API = '/api';
let categories = [];
let products = [];
let coberturas = [];
let charolas = [];
let cart = {};
let cobState = {};

function getCSRF() {
  const m = document.cookie.match(/csrftoken=([^;]+)/);
  return m ? m[1] : '';
}

function imgFallback(img, emoji) {
  img.outerHTML = `<div class="card-img" style="display:flex;align-items:center;justify-content:center;font-size:70px;background:linear-gradient(135deg,rgba(244,143,177,.4),rgba(255,220,238,.6))">${emoji}</div>`;
}

async function loadCatalog() {
  try {
    const [catRes, pRes, cRes, chRes] = await Promise.all([
      fetch(`${API}/categories/`),
      fetch(`${API}/products/`),
      fetch(`${API}/coberturas/`),
      fetch(`${API}/charolas/`),
    ]);
    categories = await catRes.json();
    products = await pRes.json();
    coberturas = await cRes.json();
    charolas = await chRes.json();

    charolas.forEach(ch => {
      cobState[ch.product_id] = {};
      coberturas.forEach(c => { cobState[ch.product_id][c.id] = 0; });
    });

    render();
  } catch (e) {
    document.getElementById('tabs-wrap').innerHTML = '';
    document.getElementById('main').innerHTML =
      '<div class="glass" style="text-align:center;padding:50px 30px;margin-top:20px">' +
      '<div style="font-size:52px;margin-bottom:14px">😢</div>' +
      '<p style="color:var(--t2);margin-bottom:20px;font-size:14px;line-height:1.6">No pudimos cargar el menú.<br>Verifica tu conexión.</p>' +
      '<button class="btn btn-primary" onclick="loadCatalog()" style="padding:12px 30px;font-size:15px">🔄 Reintentar</button></div>';
  }
}

function safe(v, fallback='') { return v != null ? v : fallback; }

function render() {
  if (!categories || !categories.length) return;

  const tabsWrap = document.getElementById('tabs-wrap');
  tabsWrap.innerHTML = `<div class="tabs">${categories.map((c, i) =>
    `<button class="tab-btn${i === 0 ? ' active' : ''}" onclick="showTab('cat-${c.id}',this)">${safe(c.emoji,'🍩')} ${safe(c.name)}</button>`
  ).join('')}</div>`;

  const main = document.getElementById('main');
  main.innerHTML = categories.map((c, i) => `
    <section id="cat-${c.id}" class="section${i === 0 ? ' active' : ''}">
      <div class="sec-head glass">
        <div class="sec-icon">${safe(c.emoji,'🍩')}</div>
        <div><h2>${safe(c.name)}</h2><p>${safe(c.description)}</p></div>
      </div>
      <div class="prod-list">${(products || []).filter(p => p && p.category && p.category.id === c.id).map(p => renderCard(p)).join('')}</div>
    </section>
  `).join('');

  updateCartUI();
}

function renderCard(p) {
  const ch = charolas.find(x => x.product_id === p.id);
  if (ch) return renderCharolaCard(p, ch);

  return `
    <div class="card">
      <img class="card-img" src="${p.image_url || ''}" alt="${p.name}"
        onerror="imgFallback(this,'${p.emoji}')">
      <div class="card-body">
        <div class="card-top">
          <div class="card-name">${p.name}</div>
          <div class="card-price" id="price-${p.id}">$${p.price}</div>
        </div>
        ${p.description ? `<div class="card-desc">${p.description}</div>` : ''}
        <div class="qty-row">
          <div class="qty-ctrl">
            <button class="qty-btn" onclick="changeQty(${p.id},-1)">−</button>
            <span class="qty-num" id="qty-${p.id}">1</span>
            <button class="qty-btn" onclick="changeQty(${p.id},1)">+</button>
          </div>
          <button class="btn btn-primary add-btn" onclick="addToCart(${p.id})">🛒 Agregar</button>
        </div>
      </div>
    </div>`;
}

function renderCharolaCard(p, ch) {
  return `
    <div class="card">
      <img class="card-img" src="${p.image_url || ''}" alt="${p.name}"
        onerror="imgFallback(this,'${p.emoji}')">
      <div class="card-body">
        <div class="card-top">
          <div class="card-name">${p.name}</div>
          <div class="card-price" id="price-${p.id}">$${p.price}</div>
        </div>
        ${p.description ? `<div class="card-desc">${p.description}</div>` : ''}

        <div class="prog-wrap">
          <div class="prog-bar-bg">
            <div class="prog-bar-fill" id="prog-${p.id}" style="width:0%"></div>
          </div>
          <div class="prog-label">
            <span>Donas asignadas:</span>
            <span id="assigned-${p.id}" class="prog-count">0 / ${ch.size}</span>
          </div>
        </div>

        <div class="cob-rows">
          ${coberturas.map(c => `
            <div class="cob-row">
              <div class="cob-row-info">
                <span class="cob-row-emoji">${c.emoji}</span>
                <div>
                  <div class="cob-row-name">${c.name}</div>
                  <div class="cob-row-price">$${c.price} × dona</div>
                </div>
              </div>
              <div class="qty-ctrl">
                <button class="qty-btn" onclick="changeCob(${p.id},${c.id},-1)">−</button>
                <span class="qty-num" id="cob-${p.id}-${c.id}">0</span>
                <button class="qty-btn" onclick="changeCob(${p.id},${c.id},1)">+</button>
              </div>
            </div>
          `).join('')}
        </div>

        <button class="btn btn-primary add-btn" id="btn-${p.id}"
          onclick="addCharolaToCart(${p.id})" disabled
          style="width:100%;margin-top:8px;padding:13px;font-size:14.5px">
          🛒 Asigna las ${ch.size} donas para agregar
        </button>
      </div>
    </div>`;
}

function showTab(id, btn) {
  document.querySelectorAll('.section').forEach(s => s.classList.remove('active'));
  document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
  const el = document.getElementById(id);
  if (el) el.classList.add('active');
  if (btn) btn.classList.add('active');
  window.scrollTo({ top: 0, behavior: 'smooth' });
}

function changeQty(id, delta) {
  const el = document.getElementById('qty-' + id);
  let q = parseInt(el.textContent) || 1;
  q = Math.max(1, q + delta);
  el.textContent = q;
}

function getCobTotal(pid) {
  const s = cobState[pid] || {};
  return Object.values(s).reduce((a, b) => a + b, 0);
}

function getCobPrice(pid) {
  const s = cobState[pid] || {};
  return Object.entries(s).reduce((sum, [cid, qty]) => {
    const c = coberturas.find(x => x.id === parseInt(cid));
    return sum + (c ? c.price * qty : 0);
  }, 0);
}

function changeCob(pid, cid, delta) {
  const ch = charolas.find(x => x.product_id === pid);
  if (!ch) return;
  const total = getCobTotal(pid);
  if (delta > 0 && total >= ch.size) { toast('⚠️ Ya asignaste todas las donas'); return; }
  cobState[pid][cid] = Math.max(0, (cobState[pid][cid] || 0) + delta);
  updateCobUI(pid);
}

function updateCobUI(pid) {
  const ch = charolas.find(x => x.product_id === pid);
  if (!ch) return;
  const p = products.find(x => x.id === pid);
  if (!p) return;
  const assigned = getCobTotal(pid);
  const extra = getCobPrice(pid);
  const total = parseFloat(p.price) + extra;

  coberturas.forEach(c => {
    const el = document.getElementById(`cob-${pid}-${c.id}`);
    if (el) el.textContent = cobState[pid][c.id] || 0;
  });

  document.getElementById(`price-${pid}`).textContent = '$' + total;
  document.getElementById(`prog-${pid}`).style.width = ((assigned / ch.size) * 100) + '%';
  const lbl = document.getElementById(`assigned-${pid}`);
  lbl.textContent = `${assigned} / ${ch.size}`;
  lbl.classList.toggle('complete', assigned === ch.size);

  const btn = document.getElementById(`btn-${pid}`);
  const ready = assigned === ch.size;
  const remain = ch.size - assigned;
  btn.disabled = !ready;
  btn.textContent = ready
    ? '🛒 Agregar al Carrito'
    : `🛒 Asigna ${remain} dona${remain !== 1 ? 's' : ''} más`;
}

function addToCart(pid) {
  const p = products.find(x => x.id === pid);
  if (!p) return;
  const qtyEl = document.getElementById('qty-' + pid);
  const qty = parseInt(qtyEl ? qtyEl.textContent : 1);
  const key = 'p' + pid;
  if (cart[key]) cart[key].qty += qty;
  else cart[key] = { name: p.name, price: parseFloat(p.price), emoji: p.emoji, qty, detail: '' };
  if (qtyEl) qtyEl.textContent = 1;
  updateCartUI();
  toast(p.emoji + ' Agregado al carrito');
}

function addCharolaToCart(pid) {
  const ch = charolas.find(x => x.product_id === pid);
  const p = products.find(x => x.id === pid);
  if (!ch || !p) return;
  const assigned = getCobTotal(pid);
  if (assigned !== ch.size) { toast('⚠️ Asigna todas las donas primero'); return; }

  const extra = getCobPrice(pid);
  const total = parseFloat(p.price) + extra;
  const mix = Object.entries(cobState[pid])
    .filter(([, v]) => v > 0)
    .map(([cid, v]) => {
      const c = coberturas.find(x => x.id === parseInt(cid));
      return `${v} ${c ? c.name : ''}`;
    }).join(', ');

  const key = 'ch' + pid + '-' + Date.now();
  cart[key] = { name: p.name, price: total, emoji: p.emoji, detail: mix, qty: 1 };

  Object.keys(cobState[pid]).forEach(k => cobState[pid][k] = 0);
  updateCobUI(pid);
  updateCartUI();
  toast('🍩 Charola agregada al carrito');
}

function updateCartUI() {
  const entries = Object.entries(cart).filter(([, v]) => v.qty > 0);
  const total = entries.reduce((s, [, v]) => s + v.price * v.qty, 0);
  const count = entries.reduce((s, [, v]) => s + v.qty, 0);

  const badge = document.getElementById('cart-badge');
  badge.textContent = count;
  badge.classList.toggle('hidden', count === 0);

  const list = document.getElementById('cart-list');
  const footer = document.getElementById('cart-footer');

  if (count === 0) {
    list.innerHTML = '<div class="cart-empty-msg"><div>🛒</div>Tu carrito está vacío</div>';
    footer.style.display = 'none';
    return;
  }

  footer.style.display = 'block';
  document.getElementById('cart-total-val').textContent = total + '$';

  list.innerHTML = entries.map(([id, item]) => `
    <div class="citem glass">
      <div class="citem-info">
        <div class="citem-name">${item.emoji || '•'} ${item.name}</div>
        <div class="citem-sub">${item.detail ? item.detail + ' — ' : ''}${item.qty} × $${item.price} = $${item.qty * item.price}</div>
      </div>
      <div class="citem-price">$${item.qty * item.price}</div>
      <button class="citem-del" onclick="removeFromCart('${id}')">×</button>
    </div>
  `).join('');
}

function removeFromCart(id) {
  delete cart[id];
  updateCartUI();
}

function toggleCart() {
  const p = document.getElementById('cart-panel');
  const o = document.getElementById('overlay');
  document.getElementById('order-modal').classList.remove('open');
  const isOpen = p.classList.toggle('open');
  o.classList.toggle('show', isOpen);
}

function closeCart() {
  document.getElementById('cart-panel').classList.remove('open');
  document.getElementById('overlay').classList.remove('show');
}

function openOrder() {
  closeCart();
  setTimeout(() => {
    const entries = Object.entries(cart).filter(([, v]) => v.qty > 0);
    const total = entries.reduce((s, [, v]) => s + v.price * v.qty, 0);
    document.getElementById('order-summary').innerHTML =
      '<strong>Resumen:</strong><br>' +
      entries.map(([, v]) => `${v.emoji || '•'} ${v.name} ×${v.qty} = $${v.qty * v.price}`).join('<br>') +
      `<br><strong style="color:var(--p1)">Total: $${total}</strong>`;
    document.getElementById('order-modal').classList.add('open');
    document.getElementById('overlay').classList.add('show');
  }, 310);
}

function closeOrder() {
  document.getElementById('order-modal').classList.remove('open');
  document.getElementById('overlay').classList.remove('show');
}

async function submitOrder() {
  const name = document.getElementById('order-name').value.trim();
  const phone = document.getElementById('order-phone').value.trim();
  if (!name) { toast('⚠️ Escribe tu nombre'); return; }
  if (!phone) { toast('⚠️ Escribe tu teléfono'); return; }

  const entries = Object.entries(cart).filter(([, v]) => v.qty > 0);
  const total = entries.reduce((s, [, v]) => s + v.price * v.qty, 0);

  const items = entries.map(([, v]) => ({
    name: v.name, qty: v.qty, price: v.price, emoji: v.emoji || '',
    detail: v.detail || '',
  }));

  try {
    const res = await fetch(`${API}/orders/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCSRF() },
      body: JSON.stringify({ customer_name: name, customer_phone: phone, items, total }),
    });

    if (!res.ok) {
      const err = await res.json();
      toast('⚠️ Error: ' + (err.customer_name ? err.customer_name[0] : 'Intenta de nuevo'));
      return;
    }

    document.getElementById('confirm-phone').textContent = phone;
    closeOrder();
    document.getElementById('confirm-modal').classList.add('open');
    document.getElementById('overlay').classList.add('show');
    cart = {};
    updateCartUI();
    document.getElementById('order-name').value = '';
    document.getElementById('order-phone').value = '';
  } catch (e) {
    toast('⚠️ Error de conexión');
  }
}

function closeConfirm() {
  document.getElementById('confirm-modal').classList.remove('open');
  document.getElementById('overlay').classList.remove('show');
}

function closeAll() {
  closeCart();
  closeOrder();
  closeConfirm();
}

function toast(msg) {
  const t = document.getElementById('toast');
  t.textContent = msg;
  t.classList.add('show');
  setTimeout(() => t.classList.remove('show'), 2400);
}

document.addEventListener('DOMContentLoaded', loadCatalog);
document.addEventListener('keydown', e => { if (e.key === 'Escape') closeAll(); });
