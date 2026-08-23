export default function Header({ vista, onVista, onLogout }) {
  const botones = [
    ["eventos", "Eventos"],
    ["tabla", "Tabla"],
    ["stats", "Stats"],
  ];
  return (
    <header>
      <div className="brand">
        <img src="/assets/logo.png" alt="" className="logo-img" />
        <span className="wordmark">ipOna</span>
      </div>
      <nav>
        {botones.map(([id, label]) => (
          <button
            key={id}
            className={vista === id ? "activo" : ""}
            onClick={() => onVista(id)}
          >
            {label}
          </button>
        ))}
        <button onClick={onLogout}>Salir</button>
      </nav>
    </header>
  );
}
