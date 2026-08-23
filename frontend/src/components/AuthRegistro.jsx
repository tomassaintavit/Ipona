import { useState } from "react";
import { api, setToken } from "../api.js";

async function login(username, password) {
  const res = await fetch("/auth/login", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, password }),
  });
  if (!res.ok) throw new Error("Cuenta creada. Ingresá manualmente.");
  return (await res.json()).access_token;
}

export default function AuthRegistro({ onLogin }) {
  const [error, setError] = useState("");

  async function handleSubmit(ev) {
    ev.preventDefault();
    const f = ev.target;
    setError("");
    try {
      await api("/auth/register", {
        method: "POST",
        body: JSON.stringify({
          email: f.email.value,
          username: f.username.value,
          password: f.password.value,
        }),
      });
      setToken(await login(f.username.value, f.password.value));
      onLogin(true);
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <>
      <div className="auth-hero chico">
        <img src="/assets/logo.png" alt="" className="auth-logo" />
        <span className="wordmark">ipOna</span>
        <p className="tagline">Sumate a la competencia</p>
      </div>
      <form className="card form-card" onSubmit={handleSubmit}>
        <label>
          Email
          <input name="email" type="email" placeholder="vos@mail.com" required />
        </label>
        <label>
          Usuario
          <input name="username" placeholder="mínimo 3 caracteres" required minLength={3} pattern="[a-zA-Z0-9_]+" />
        </label>
        <label>
          Contraseña
          <input name="password" type="password" placeholder="mínimo 8 caracteres" required minLength={8} />
        </label>
        <button type="submit">Crear cuenta</button>
        {error && <p className="error">{error}</p>}
      </form>
    </>
  );
}
