import { useState } from "react";

const ICONOS = {
  eventos: (
    <svg viewBox="0 0 24 24" width="17" height="17" fill="currentColor" aria-hidden="true">
      <path d="M19 4h-1V2h-2v2H8V2H6v2H5a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V6a2 2 0 0 0-2-2zm0 16H5V10h14v10zM5 8V6h14v2H5z" />
    </svg>
  ),
  tabla: (
    <svg viewBox="0 0 24 24" width="17" height="17" fill="currentColor" aria-hidden="true">
      <path d="M5 3h14a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2zm3 15a1 1 0 1 0 0-2 1 1 0 0 0 0 2zm9-8h-9v2h9v-2z" />
    </svg>
  ),
  historico: (
    <svg viewBox="0 0 24 24" width="17" height="17" fill="currentColor" aria-hidden="true">
      <path d="M12 2a10 10 0 1 0 0 20 10 10 0 0 0 0-20zm0 18a8 8 0 1 1 0-16 8 8 0 0 1 0 16zm1-13h-2v6l5.25 3.15 1-1.65-4.25-2.5V7z" />
    </svg>
  ),
  stats: (
    <svg viewBox="0 0 24 24" width="17" height="17" fill="currentColor" aria-hidden="true">
      <path d="M3 3h2v18H3V3zm4 6h2v12H7V9zm4 3h2v9h-2v-9zm4 3h2v6h-2v-6zm4-6h2v12h-2V9z" />
    </svg>
  ),
  salir: (
    <svg viewBox="0 0 24 24" width="17" height="17" fill="currentColor" aria-hidden="true">
      <path d="M17 7l-1.41 1.41L18.17 11H8v2h10.17l-2.58 2.58L17 17l5-5-5-5zM4 5h8V3H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h8v-2H4V5z" />
    </svg>
  ),
};

export default function Header({ vista, onVista, onLogout }) {
  const [menuAbierto, setMenuAbierto] = useState(false);
  const botones = [
    { id: "eventos", label: "Eventos", icono: ICONOS.eventos },
    { id: "tabla", label: "Tabla", icono: ICONOS.tabla },
    { id: "historico", label: "Histórico", icono: ICONOS.historico },
    { id: "stats", label: "Estadísticas", icono: ICONOS.stats },
  ];

  function elegir(id) {
    setMenuAbierto(false);
    onVista(id);
  }

  return (
    <header>
      <div className="brand">
        <img src="/assets/logo.png" alt="" className="logo-img" />
        <span className="wordmark">ipOna</span>
      </div>
      <button
        className={`hamburguesa ${menuAbierto ? "abierto" : ""}`}
        onClick={() => setMenuAbierto((o) => !o)}
        aria-label="Abrir menú"
        aria-expanded={menuAbierto}
      >
        <span />
        <span />
        <span />
      </button>
      <nav className={menuAbierto ? "abierto" : ""}>
        {botones.map(({ id, label, icono }) => (
          <button key={id} className={vista === id ? "activo" : ""} onClick={() => elegir(id)}>
            {icono}
            <span>{label}</span>
          </button>
        ))}
        <button className="salir" onClick={() => { setMenuAbierto(false); onLogout(); }}>
          {ICONOS.salir}
          <span>Salir</span>
        </button>
      </nav>
    </header>
  );
}