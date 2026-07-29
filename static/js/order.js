/* SVS Stock App – Bestelskerm logika */

function switchTab(name, btn) {
  document.querySelectorAll('.tab-panel').forEach(p => p.classList.remove('active'));
  document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
  document.getElementById('tab-' + name).classList.add('active');
  btn.classList.add('active');
}

function changeQty(cardId, delta) {
  const input = document.getElementById('qty-' + cardId);
  if (!input) return;
  let val = Math.max(0, (parseInt(input.value) || 0) + delta);
  input.value = val;
  const card = document.getElementById(cardId);
  if (card) card.classList.toggle('selected', val > 0);
}

// ── Eenmalige / aangepaste items ──
function addCustom(prefix, cat) {
  var container = document.getElementById(prefix + '-custom');
  var div = document.createElement('div');
  div.className = 'custom-item-row';
  div.innerHTML =
    '<span class="custom-badge">✱ Eenmalig</span>' +
    '<input type="text" class="custom-name" placeholder="Produk naam..." data-cat="' + cat + '">' +
    '<div style="display:flex;gap:.4rem;align-items:center;">' +
      '<label style="font-size:.78rem;color:#7A6B8A;white-space:nowrap;">Hoev:</label>' +
      '<input type="number" class="custom-qty" value="1" min="1" max="999">' +
    '</div>' +
    '<input type="text" class="custom-note" placeholder="Nota (opsioneel)">' +
    '<button type="button" class="custom-remove" onclick="this.parentElement.remove()" title="Verwyder">×</button>';
  container.appendChild(div);
  // Fokus op die naam-invoer
  div.querySelector('.custom-name').focus();
}

// ── Produk soek (per-tab) ──
function filterProducts(gridId, query) {
  var q = query.toLowerCase();
  document.querySelectorAll('#' + gridId + ' .product-card').forEach(function(card) {
    var match = (card.dataset.search || card.dataset.name || '').toLowerCase().includes(q);
    card.style.display = (!q || match) ? '' : 'none';
  });
}

// ── Globale soek (alle kategorieë) ──
function globalSearch(query) {
  var panel   = document.getElementById('global-search-panel');
  var tabsEl  = document.querySelector('.tabs');
  var panels  = document.querySelectorAll('.tab-panel');
  var q       = query.trim().toLowerCase();

  if (!q) {
    panel.style.display = 'none';
    tabsEl.style.display = '';
    panels.forEach(function(p) { p.style.display = ''; }); // laat CSS .active oorneem
    return;
  }

  // Verberg tabs, wys soekresultate
  tabsEl.style.display = 'none';
  panels.forEach(function(p) { p.style.display = 'none'; });
  panel.style.display = 'block';

  var grid  = document.getElementById('global-results-grid');
  var count = document.getElementById('global-search-count');
  grid.innerHTML = '';
  var found = 0;

  document.querySelectorAll('.product-grid .product-card').forEach(function(card) {
    var name = (card.dataset.search || card.dataset.name || '').toLowerCase();
    if (!name.includes(q)) return;
    found++;

    var origId     = card.id;
    var origInput  = document.getElementById('qty-' + origId);
    var qty        = origInput ? (parseInt(origInput.value) || 0) : 0;
    var cat        = card.dataset.cat || '';

    var div = document.createElement('div');
    div.className = 'product-card' + (qty > 0 ? ' selected' : '');
    div.id = 'sr-' + origId;
    div.innerHTML =
      '<div class="product-name">' + (card.dataset.name || '') + '</div>' +
      '<div style="font-size:.7rem;color:#9B59B6;font-weight:600;margin:.1rem 0 .35rem;">' + cat + '</div>' +
      '<div class="qty-ctrl">' +
        '<button type="button" class="qty-btn" onclick="srChange(\'' + origId + '\',-1)">−</button>' +
        '<span id="srd-' + origId + '" style="min-width:2rem;text-align:center;font-weight:700;font-size:1rem;display:inline-block;">' + qty + '</span>' +
        '<button type="button" class="qty-btn" onclick="srChange(\'' + origId + '\',1)">+</button>' +
      '</div>';
    grid.appendChild(div);
  });

  if (count) count.textContent = found ? found + ' produk(te) gevind' : '';
  if (!found) {
    grid.innerHTML = '<p style="color:#9B8AAA;padding:.25rem 0;">Geen produkte gevind nie.</p>';
  }
}

// Verander qty via soekresultaat — sync na die werklike kaart
function srChange(origId, delta) {
  changeQty(origId, delta);
  var origInput = document.getElementById('qty-' + origId);
  var qty = origInput ? (parseInt(origInput.value) || 0) : 0;
  var disp = document.getElementById('srd-' + origId);
  if (disp) disp.textContent = qty;
  var mirror = document.getElementById('sr-' + origId);
  if (mirror) mirror.classList.toggle('selected', qty > 0);
}

// ── Versamel items en stuur vorm na bediener ──
function prepareAndSubmit() {
  try {
    var items = [];

    // Katalogus produkte (gewone items)
    document.querySelectorAll('.product-card').forEach(function(card) {
      var input = card.querySelector('.qty-input');
      var qty = parseInt(input ? input.value : 0) || 0;
      if (qty > 0) {
        items.push({ name: card.dataset.name, category: card.dataset.cat,
                     quantity: qty, note: '', is_custom: 0 });
      }
    });

    // Eenmalige / aangepaste items
    document.querySelectorAll('.custom-item-row').forEach(function(row) {
      var name = row.querySelector('.custom-name');
      var qty  = row.querySelector('.custom-qty');
      var note = row.querySelector('.custom-note');
      var nameVal = name ? name.value.trim() : '';
      if (nameVal) {
        items.push({
          name:      nameVal,
          category:  name.dataset.cat || 'Salon',
          quantity:  parseInt(qty ? qty.value : 1) || 1,
          note:      note ? note.value.trim() : '',
          is_custom: 1
        });
      }
    });

    // Handoeke — stoor ALTYD alle vaste tipes (selfs met qty=0 sodat die afdeling altyd sigbaar is)
    document.querySelectorAll('.towel-qty-input').forEach(function(input) {
      var qty = parseFloat(input.value) || 0;
      var row = input.closest('tr');
      var noteInput = row ? row.querySelector('.towel-note-input') : null;
      var note = noteInput ? noteInput.value.trim() : '';
      items.push({
        name:      input.dataset.towelType,
        category:  'Handoeke',
        quantity:  qty,
        note:      note,
        is_custom: 0
      });
    });

    // Ekstra / aangepaste handoek-tipes (gebruiker het self bygevoeg)
    document.querySelectorAll('.custom-towel-row').forEach(function(row) {
      var nameEl = row.querySelector('.towel-custom-name');
      var qtyEl  = row.querySelector('.towel-custom-qty');
      var noteEl = row.querySelector('.towel-custom-note');
      var name   = nameEl ? nameEl.value.trim() : '';
      var qty    = qtyEl  ? (parseFloat(qtyEl.value) || 0) : 0;
      var note   = noteEl ? noteEl.value.trim() : '';
      if (name && qty > 0) {
        items.push({ name: name, category: 'Handoeke', quantity: qty, note: note, is_custom: 1 });
      }
    });

    // Geld as leeg as daar geen produkte/tints/retail items is EN geen handoeke met qty > 0
    var hasRealItems = items.some(function(i) {
      return i.category !== 'Handoeke' && i.quantity > 0;
    });
    var hasTowels = items.some(function(i) {
      return i.category === 'Handoeke' && i.quantity > 0;
    });
    if (!hasRealItems && !hasTowels) {
      alert('Kies asseblief ten minste een item voor jy die bestelling stuur.');
      return;
    }

    document.getElementById('itemsJson').value = JSON.stringify(items);
    document.getElementById('orderForm').submit();
  } catch(e) {
    alert('Fout: ' + e.message);
    console.error(e);
  }
}
