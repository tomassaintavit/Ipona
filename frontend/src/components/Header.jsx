import { useState } from "react";

export default function Header({ vista, onVista, onLogout }) {
  const [menuAbierto, setMenuAbierto] = useState(false);
  const botones = [
    ["eventos", "Eventos"],
    ["tabla", "Tabla"],
    ["stats", "Estadísticas"],
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
        {botones.map(([id, label]) => (
          <button
            key={id}
            className={vista === id ? "activo" : ""}
            onClick={() => elegir(id)}
          >
            {label}
          </button>
        ))}
        <button
          onClick={() => {
            setMenuAbierto(false);
            onLogout();
          }}
        >
          Salir
        </button>
      </nav>
    </header>
  );
}
