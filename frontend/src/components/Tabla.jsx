import { useEffect, useState } from "react";
import { api } from "../api.js";

const COLORES_AVATAR = ["#6d4ba3", "#8b5cf6", "#a582d4", "#5b21b6", "#c084fc"];

const COLORES_DEPORTE = {
  futbol: ["#7c3aed", "#c084fc"],
  basquet: ["#0ea5e9", "#67e8f9"],
  formula_1: ["#ef4444", "#fb7185"],
};

const NOMBRES_DEPORTE = {
  futbol: "Fútbol",
  basquet: "NBA",
  formula_1: "F1",
};

const ORDEN_DEPORTE = ["futbol", "basquet", "formula_1"];

function iniciales(nombre) {
  return (
    nombre
      .split(/\s+/)
      .slice(0, 2)
      .map((w) => w[0])
      .join("")
      .toUpperCase()
  );
}

function colorAvatar(nombre) {
  let h = 0;
  for (const c of nombre) h = (h * 31 + c.charCodeAt(0)) >>> 0;
  return COLORES_AVATAR[h % COLORES_AVATAR.length];
}

function Avatar({ nombre, ia }) {
  const bg = ia ? "linear-gradient(135deg, #5b21b6, #a855f7)" : colorAvatar(nombre);
  return (
    <span className={`avatar${ia ? " ia" : ""}`} style={{ background: bg }}>
      {iniciales(nombre)}
    </span>
  );
}

function Corona() {
  return (
    <svg viewBox="0 0 24 24" width="15" height="15" fill="#ffd75e" aria-hidden="true">
      <path d="M3 7l4.2 4L12 5l4.8 6L21 7v10H3V7z" />
    </svg>
  );
}

function BarraDeportes({ sports, max, mini }) {
  return (
    <div className={`barra-pts${mini ? " mini" : ""}`}>
      {ORDEN_DEPORTE.map((deporte) => {
        const pts = sports?.[deporte];
        if (!pts) return null;
        const pct = Math.min(100, Math.round((pts / max) * 100));
        const [c1, c2] = COLORES_DEPORTE[deporte];
        return (
          <span
            key={deporte}
            title={`${NOMBRES_DEPORTE[deporte]}: ${pts} pts`}
            style={{
              width: `${pct}%`,
              background: `linear-gradient(90deg, ${c1}, ${c2})`,
            }}
          />
        );
      })}
    </div>
  );
}

function PodiumCard({ fila, max }) {
  const gap = fila.position === 1 ? null : (max - fila.total_points).toFixed(1);
  return (
    <div
      className={`podio-card p${fila.position}`}
      style={{ animationDelay: `${(fila.position - 1) * 90}ms` }}
    >
      <div className="puesto-ranking">
        {fila.position === 1 && <Corona />}
        {fila.position}°
      </div>
      <Avatar nombre={fila.username} ia={fila.is_llm} />
      <div className="podio-nombre">
        {fila.username}
        {fila.is_llm && <span className="chip-ia">IA</span>}
      </div>
      <div className="podio-puntos">{fila.total_points}</div>
      <div className="podio-puntos-label">puntos</div>
      <BarraDeportes sports={fila.puntos_por_deporte} max={max} />
      <div className="podio-meta">
        <span>{fila.predictions} preds</span>
        <span>{gap === null ? "¡Líder!" : `${gap} pts del 1°`}</span>
      </div>
    </div>
  );
}

function Fila({ fila, max, index }) {
  const gap = (max - fila.total_points).toFixed(1);
  return (
    <div className="fila-tabla" style={{ animationDelay: `${index * 45}ms` }}>
      <span className="posicion">{fila.position}</span>
      <Avatar nombre={fila.username} ia={fila.is_llm} />
      <div className="fila-info">
        <div className="fila-nombre">
          {fila.username}
          {fila.is_llm && <span className="chip-ia">IA</span>}
        </div>
        <BarraDeportes sports={fila.puntos_por_deporte} max={max} mini />
      </div>
      <div className="fila-puntos">
        {fila.total_points}
        <small> pts</small>
      </div>
      <div className="fila-gap">−{gap}</div>
    </div>
  );
}

export default function Tabla({ onToast }) {
  const [board, setBoard] = useState(null);
  const [period, setPeriod] = useState("global");

  useEffect(() => {
    setBoard(null);
    api(`/leaderboard?period=${period}`)
      .then(setBoard)
      .catch((err) => onToast(err.message));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [period]);

  if (board === null) return <div className="cargando">Cargando tabla…</div>;
  if (board.length === 0)
    return <p className="nota">Todavía no hay jugadores en la tabla.</p>;

  const max = Math.max(...board.map((f) => f.total_points), 1);

  return (
    <section className="tabla">
      <div className="tabla-header">
        <div>
          <h2>Tabla de posiciones</h2>
          <p>Se puntúa al finalizar cada partido.</p>
        </div>
        <span className="chip-vivos">{board.length} jugadores</span>
      </div>

      <div className="tabs">
        {[
          { id: "global", label: "Global" },
          { id: "weekly", label: "Semanal" },
          { id: "monthly", label: "Mensual" },
        ].map((t) => (
          <button
            key={t.id}
            className={period === t.id ? "activo" : ""}
            onClick={() => setPeriod(t.id)}
          >
            {t.label}
          </button>
        ))}
      </div>

      {(() => {
        const deportesPresentes = new Set();
        for (const f of board) {
          for (const d of ORDEN_DEPORTE) {
            if (f.puntos_por_deporte?.[d]) deportesPresentes.add(d);
          }
        }
        if (deportesPresentes.size > 1) {
          return (
            <div className="leyenda">
              {ORDEN_DEPORTE.filter((d) => deportesPresentes.has(d)).map((d) => {
                const [c1, c2] = COLORES_DEPORTE[d];
                return (
                  <span className="leyenda-item" key={d}>
                    <i style={{ background: `linear-gradient(90deg, ${c1}, ${c2})` }} />
                    {NOMBRES_DEPORTE[d]}
                  </span>
                );
              })}
            </div>
          );
        }
        return null;
      })()}

      <div className="podio">
        {board.slice(0, 3).map((f) => (
          <PodiumCard key={f.username} fila={f} max={max} />
        ))}
      </div>

      {board.length > 3 && (
        <div className="tabla-lista">
          {board.slice(3).map((f, i) => (
            <Fila key={f.username} fila={f} max={max} index={i} />
          ))}
        </div>
      )}

      <p className="nota">Las predicciones se puntúan al finalizar cada partido.</p>
    </section>
  );
}