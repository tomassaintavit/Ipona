const API = "";

let token = localStorage.getItem("ipona_token");

export function getToken() {
  return token;
}

export function setToken(t) {
  token = t;
  if (t) localStorage.setItem("ipona_token", t);
  else localStorage.removeItem("ipona_token");
}

export async function api(path, options = {}) {
  const headers = { "Content-Type": "application/json", ...(options.headers || {}) };
  const current = getToken();
  if (current) headers.Authorization = `Bearer ${current}`;
  const res = await fetch(API + path, { ...options, headers });
  if (res.status === 401 && getToken()) {
    setToken(null);
    window.location.reload();
    throw new Error("Sesión expirada");
  }
  if (!res.ok) {
    const detail = await res.json().catch(() => ({}));
    throw new Error(detail.detail || `Error ${res.status}`);
  }
  return res.json();
}
