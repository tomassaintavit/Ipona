import { useState } from "react";
import { api } from "../api.js";

export default function AuthLogin({ onLogin, irARegistro }) {
  const [error, setError] = useState("");

  async function handleSubmit(ev) {
    ev.preventDefault();
    const f = ev.target;
    setError("");
    try {
      const res = await fetch("/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          username: f.username.value,
          password: f.password.value,
        }),
      });
      if (!res.ok) {
        const detail = await res.json().catch(() => ({}));
        throw new Error(detail.detail || `Error ${res.status}`);
      }
      onLogin((await res.json()).access_token);
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <>
      <div className="auth-hero">
        <img src="/assets/logo.png" alt="" className="auth-logo" />
        <span className="wordmark grande">ipOna</span>
      </div>
      <form className="card form-card" onSubmit={handleSubmit}>
        <label>
          Usuario
          <input name="username" placeholder="tu usuario" required autoComplete="username" />
        </label>
        <label>
          Contraseña
          <input name="password" type="password" placeholder="••••••••" required autoComplete="current-password" />
        </label>
        <button type="submit">Ingresar</button>
        {error && <p className="error">{error}</p>}
        <p className="cambio-vista">
          ¿No tenés cuenta?{" "}
          <a href="#" onClick={(e) => { e.preventDefault(); irARegistro(); }}>
            Creá una
          </a>
        </p>
      </form>
    </>
  );
}
