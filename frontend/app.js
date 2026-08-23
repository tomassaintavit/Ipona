const $ = (sel) => document.querySelector(sel);
const API = "";

let token = localStorage.getItem("ipona_token");
let vista = "eventos";

async function api(path, options = {}) {
  const headers = { "Content-Type": "application/json", ...(options.headers || {}) };
  if (token) headers.Authorization = `Bearer ${token}`;
  const res = await fetch(API + path, { ...options, headers });
  if (res.status === 401 && token) { logout(); throw new Error("sesion expirada"); }
  if (!res.ok) {
    const detail = await res.json().catch(() => ({}));
    throw new Error(detail.detail || `error ${res.status}`);
  }
  return res.json();
}

function toast(msg) {
  const el = $("#toast");
  el.textContent = msg;
  el.classList.remove("hidden");
  setTimeout(() => el.classList.add("hidden"), 2500);
}

function mostrarVista(nombre) {
  vista = nombre;
  document.querySelectorAll(".view").forEach(v => v.classList.add("hidden"));
  $("#view-" + nombre).classList.remove("hidden");
  document.querySelectorAll("nav button[data-view]").forEach(b =>
    b.classList.toggle("activo", b.dataset.view === nombre));
  if (nombre === "eventos") cargarEventos();
  if (nombre === "tabla") cargarTabla();
  if (nombre === "stats") cargarStats();
}

function loginOK(t) {
  token = t;
  localStorage.setItem("ipona_token", t);
  $("#nav").classList.remove("hidden");
  $("#view-auth").classList.add("hidden");
  mostrarVista("eventos");
}

function logout() {
  token = null;
  localStorage.removeItem("ipona_token");
  location.reload();
}

function formatoHora(iso) {
  return new Date(iso).toLocaleString("es-AR", { day: "2-digit", month: "short", hour: "2-digit", minute: "2-digit" });
}

async function cargarEventos() {
  try {
    const eventos = await api("/events/today");
    const cont = $("#eventos-lista");
    cont.innerHTML = "";
    for (const e of eventos) {
      const card = document.createElement("div");
      card.className = "card partido";
      const titulo = e.sport === "formula_1"
        ? e.participants?.slice(0, 8).join(", ") || "Gran Premio"
        : `${e.home_team} vs ${e.away_team}`;
      card.innerHTML = `
        <div class="equipos">${titulo}</div>
        <div class="meta">${e.league} · ${formatoHora(e.start_time_utc)}</div>`;
      const form = document.createElement("form");
      form.dataset.eventId = e.id;
      form.dataset.sport = e.sport;
      if (e.sport === "formula_1") {
        const pilotos = e.participants || [];
        form.innerHTML = [0, 1, 2].map(i => `
          <select name="pos${i}" required>
            <option value="">${i + 1}°</option>
            ${pilotos.map(p => `<option value="${p}">${p}</option>`).join("")}
          </select>`).join("") + `<button type="submit">Predecir</button>`;
      } else {
        form.innerHTML = `
          <input name="home" type="number" min="0" max="99" required>
          <span>–</span>
          <input name="away" type="number" min="0" max="99" required>
          <button type="submit">Predecir</button>`;
      }
      form.addEventListener("submit", enviarPrediccion);
      card.appendChild(form);
      cont.appendChild(card);
    }
  } catch (err) { toast(err.message); }
}

async function enviarPrediccion(ev) {
  ev.preventDefault();
  const f = ev.target;
  const eventId = Number(f.dataset.eventId);
  let body;
  if (f.dataset.sport === "formula_1") {
    const positions = [f.pos0.value, f.pos1.value, f.pos2.value];
    if (new Set(positions).size !== 3) { toast("Elegí 3 pilotos distintos"); return; }
    body = { event_id: eventId, positions };
  } else {
    body = { event_id: eventId, home_score: Number(f.home.value), away_score: Number(f.away.value) };
  }
  try {
    await api("/predictions", { method: "POST", body: JSON.stringify(body) });
    toast("¡Predicción guardada!");
    f.reset();
  } catch (err) { toast(err.message); }
}

async function cargarTabla() {
  try {
    const board = await api("/leaderboard");
    const tabla = $("#tabla-posiciones");
    tabla.innerHTML = `<tr><th>#</th><th>Jugador</th><th>Pts</th><th>Preds</th></tr>` +
      board.map(fila => `
        <tr class="${fila.is_llm ? "llm" : ""}">
          <td>${fila.position}</td>
          <td>${fila.username}${fila.is_llm ? " 🤖" : ""}</td>
          <td>${fila.total_points}</td>
          <td>${fila.predictions}</td>
        </tr>`).join("");
  } catch (err) { toast(err.message); }
}

function renderStats(data, contenedorId) {
  const c = $(contenedorId);
  const filas = data.por_deporte.map(s =>
    `<div class="stat-linea"><span>${s.sport}</span><span>${s.aciertos}/${s.predicciones} (${Math.round(s.precision * 100)}%) · ${s.puntos} pts</span></div>`
  ).join("");
  c.innerHTML = `
    <div class="stat-linea"><span>Aciertos</span><span>${data.aciertos}/${data.predicciones}</span></div>
    <div class="stat-linea"><span>Precisión</span><span>${Math.round(data.precision * 100)}%</span></div>
    ${filas}
    ${data.tokens ? `<div class="stat-linea"><span>Tokens IA</span><span>${data.tokens.total} en ${data.tokens.llamadas} llamadas</span></div>` : ""}`;
}

async function cargarStats() {
  try {
    renderStats(await api("/stats/me"), "#stats-me");
    renderStats(await api("/stats/llm"), "#stats-llm");
  } catch (err) { toast(err.message); }
}

$("#form-login").addEventListener("submit", async (ev) => {
  ev.preventDefault();
  try {
    const res = await fetch("/auth/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username: ev.target.username.value, password: ev.target.password.value }),
    });
    if (!res.ok) throw new Error((await res.json()).detail);
    loginOK((await res.json()).access_token);
  } catch (err) { toast(err.message); }
});

$("#form-register").addEventListener("submit", async (ev) => {
  ev.preventDefault();
  try {
    await api("/auth/register", {
      method: "POST",
      body: JSON.stringify({
        email: ev.target.email.value,
        username: ev.target.username.value,
        password: ev.target.password.value,
      }),
    });
    toast("Registrado. Ahora ingresá.");
    ev.target.reset();
  } catch (err) { toast(err.message); }
});

document.querySelectorAll("nav button[data-view]").forEach(b =>
  b.addEventListener("click", () => mostrarVista(b.dataset.view)));
$("#logout").addEventListener("click", logout);

if ("serviceWorker" in navigator) navigator.serviceWorker.register("/sw.js");

if (token) loginOK(token);
