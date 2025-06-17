const API = 'http://localhost:5000';

// Token ve email localStorage işlemleri
function saveToken(token) {
  localStorage.setItem('token', token);
}
function saveEmail(email) {
  localStorage.setItem('email', email);
}
function getToken() {
  return localStorage.getItem('token');
}
function getEmail() {
  return localStorage.getItem('email');
}
function authHeaders() {
  return { 'Authorization': 'Bearer ' + getToken() };
}

document.addEventListener('DOMContentLoaded', () => {

  // Kayıt Olma
  const regForm = document.getElementById('register-form');
  if (regForm) {
    regForm.addEventListener('submit', async e => {
      e.preventDefault();
      const email = e.target.email.value;
      const password = e.target.password.value;
      const role = e.target.role.value;

      const res = await fetch(`${API}/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password, role })
      });

      const errorBox = document.getElementById('error-msg');
      if (errorBox) errorBox.textContent = ''; // Önce eski hatayı temizle

      if (res.ok) {
        window.location = 'login.html';
      } else {
        const err = await res.json();
        const message = err.error || 'Kayıt sırasında bir hata oldu';
        if (errorBox) {
          errorBox.textContent = message;
        } else {
          alert(message);
        }
      }
    });
  }

  // Giriş Yapma
  const loginForm = document.getElementById('login-form');
  if (loginForm) {
    loginForm.addEventListener('submit', async e => {
      e.preventDefault();
      const email = e.target.email.value;
      const password = e.target.password.value;
      const res = await fetch(`${API}/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password })
      });
      const data = await res.json();
      if (res.ok) {
        saveToken(data.token);
        saveEmail(email);
        window.location = 'index.html';
      } else {
        alert(data.error);
      }
    });
  }

  // Şifremi Unuttum
  const forgotForm = document.getElementById('forgot-form');
  if (forgotForm) {
    forgotForm.addEventListener('submit', async e => {
      e.preventDefault();
      const email = e.target.email.value;
      const res = await fetch(`${API}/forgot-password`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email })
      });
      if (res.ok) alert('Şifre yenileme maili gönderildi.');
      else alert((await res.json()).error);
    });
  }

  // Şifre Sıfırlama
  const resetForm = document.getElementById('reset-form');
  if (resetForm) {
    resetForm.addEventListener('submit', async e => {
      e.preventDefault();
      const token = new URLSearchParams(window.location.search).get('token');
      const res = await fetch(`${API}/reset-password`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ token, password: e.target.password.value })
      });
      if (res.ok) {
        alert('Şifre başarıyla güncellendi.');
        window.location = 'login.html';
      } else {
        alert((await res.json()).error);
      }
    });
  }

  // Ürünleri Listele (index.html)
  const productsList = document.getElementById('products-list');
  if (productsList) {
    (async () => {
      if (!getToken()) {
        alert('Oturum bulunamadı. Lütfen giriş yapınız.');
        window.location = 'login.html';
        return;
      }

      const profileRes = await fetch(`${API}/profile`, { headers: authHeaders() });
      const profile = await profileRes.json();
      const currentUserRole = profile.role;
      const currentUserEmail = profile.email;

      const res = await fetch(`${API}/list-products`, { headers: authHeaders() });
      const prods = await res.json();

      const cartRes = await fetch(`${API}/get-cart`, { headers: authHeaders() });
      const cart = cartRes.ok ? await cartRes.json() : [];

      if (prods.length === 0) {
        const msg = document.createElement('p');
        msg.textContent = 'Hiç ürün bulunamadı.';
        productsList.append(msg);
      }

      prods.forEach(p => {
        const div = document.createElement('div');
        div.className = 'card';

        const isOwner = p.added_by && p.added_by === currentUserEmail;

        div.innerHTML = `
          <h4>${p.product_name}</h4>
          <p>${p.price}₺</p>
          <div class="controls">
            <button class="add-cart-btn">Sepete Ekle</button>
            <button class="update-btn">Güncelle</button>
            <button class="delete-btn">Sil</button>
          </div>
        `;

        productsList.append(div);

        // Sepete Ekle
        div.querySelector('.add-cart-btn').addEventListener('click', async () => {
          const r = await fetch(`${API}/add-to-cart`, {
            method: 'POST',
            headers: { ...authHeaders(), 'Content-Type': 'application/json' },
            body: JSON.stringify({ product_id: p._id })
          });
          if (r.ok) location.reload();
          else alert((await r.json()).error);
        });

        // Güncelle ve Sil sadece supplier ve ürün sahibi için aktif
        const updateBtn = div.querySelector('.update-btn');
        const deleteBtn = div.querySelector('.delete-btn');

        if (currentUserRole === 'supplier' && isOwner) {
          updateBtn.addEventListener('click', async () => {
            const newName = prompt("Yeni ürün adı:", p.product_name);
            const newPrice = prompt("Yeni fiyat:", p.price);
            if (!newName || !newPrice) return;
            const updateRes = await fetch(`${API}/update-product/${p._id}`, {
              method: 'PUT',
              headers: { ...authHeaders(), 'Content-Type': 'application/json' },
              body: JSON.stringify({ product_name: newName, price: Number(newPrice) })
            });
            if (updateRes.ok) location.reload();
            else alert((await updateRes.json()).error);
          });

          deleteBtn.addEventListener('click', async () => {
            if (!confirm('Ürünü silmek istediğinize emin misiniz?')) return;
            const deleteRes = await fetch(`${API}/delete-product/${p._id}`, {
              method: 'DELETE',
              headers: authHeaders()
            });
            if (deleteRes.ok) location.reload();
            else alert((await deleteRes.json()).error);
          });
        } else {
          updateBtn.disabled = true;
          deleteBtn.disabled = true;
          updateBtn.title = "Bu işlem için yetkiniz yok.";
          deleteBtn.title = "Bu işlem için yetkiniz yok.";
        }
      });

      // Ürün ekleme sadece supplier için aktif
      if (currentUserRole === 'supplier') {
        document.getElementById('supplier-actions').style.display = 'block';
        document.getElementById('new-product-form').addEventListener('submit', async e => {
          e.preventDefault();
          const product_name = e.target.product_name.value;
          const price = Number(e.target.price.value);

          const addProdRes = await fetch(`${API}/add-product`, {
            method: 'POST',
            headers: { ...authHeaders(), 'Content-Type': 'application/json' },
            body: JSON.stringify({ product_name, price })
          });

          if (addProdRes.ok) location.reload();
          else alert((await addProdRes.json()).error);
        });
      }
    })();
  }

  // Profil Sayfası (profile.html)
  const profilePage = document.getElementById('profile-page');
  if (profilePage) {
    (async () => {
      const res = await fetch(`${API}/profile`, { headers: authHeaders() });
      const me = await res.json();
      document.getElementById('email-display').textContent = me.email;
      document.getElementById('role-display').textContent = me.role;
    })();
  }

  // Sepet (cart.html)
  const cartList = document.getElementById('cart-list');
  if (cartList) {
    let currentCart = [];

    (async () => {
      const res = await fetch(`${API}/get-cart`, { headers: authHeaders() });
      const data = res.ok ? await res.json() : { cart: [] };
      currentCart = data.cart;

      if (currentCart.length === 0) {
        const msg = document.createElement('p');
        msg.textContent = 'Sepetiniz boş.';
        cartList.append(msg);
      }

      currentCart.forEach(item => {
        const div = document.createElement('div');
        div.className = 'cart-item';
        div.style.display = 'flex';
        div.style.justifyContent = 'space-between';
        div.style.alignItems = 'center';
        div.style.marginBottom = '10px';

        const info = document.createElement('span');
        info.textContent = `${item.product_name || 'Ürün'}`;

        const removeBtn = document.createElement('button');
        removeBtn.textContent = 'Sepetten Çıkar';
        removeBtn.addEventListener('click', async () => {
          const r = await fetch(`${API}/delete-from-cart`, {
            method: 'POST',
            headers: { ...authHeaders(), 'Content-Type': 'application/json' },
            body: JSON.stringify({ product_id: item.product_id })
          });
          if (r.ok) location.reload();
          else alert((await r.json()).error);
        });

        div.append(info);
        div.append(removeBtn);
        cartList.append(div);
      });
    })();

    document.getElementById('checkout').addEventListener('click', async () => {
      if (!Array.isArray(currentCart) || currentCart.length === 0) {
        alert('İşleme devam edemezsiniz. Sepetiniz boş.');
        return;
      }

      const res = await fetch(`${API}/complete-cart`, {
        method: 'POST',
        headers: authHeaders()
      });
      if (res.ok) window.location = 'success.html';
      else alert((await res.json()).error || 'Sepeti onaylama başarısız.');
    });
  }

  // Navbar butonları
  ['to-home', 'to-profile', 'to-cart', 'logout'].forEach(id => {
    const btn = document.getElementById(id);
    if (!btn) return;
    btn.onclick = () => {
      if (id === 'logout') {
        localStorage.clear();
        return window.location = 'login.html';
      }
      const routes = { 'to-home': 'index.html', 'to-profile': 'profile.html', 'to-cart': 'cart.html' };
      window.location = routes[id];
    };
  });

});
