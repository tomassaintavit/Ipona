import { useEffect, useState } from "react";
import { api } from "../api.js";

const COLORES_DEPORTE = {
  futbol: "#7c3aed",
  basquet: "#0ea5e9",
  formula_1: "#ef4444",
};

const NOMBRES_DEPORTE = {
  futbol: "Fútbol",
  basquet: "NBA",
  formula_1: "F1",
};

function hasPuntos(item) {
  return item.points !== null && item.points !== undefined;
}

function compartido(teams) {
  return teams.length >= 2 ? `${teams[0]} vs ${teams[1]}` : (teams[0] || "Evento");
}

function resultadoReal(item) {
  if (item.sport === "formula_1") return item.final_positions?.join(" · ") || "—";
  if (item.final_home === null || item.final_away === null) return "—";
  return `${item.final_home} – ${item.final_away}`;
}

function prediccion(item) {
  if (item.sport === "formula_1") return item.predicted_positions?.join(" · ") || "—";
  if (item.predicted_home === null || item.predicted_away === null) return "—";
  return `${item.predicted_home} – ${item.predicted_away}`;
}

export default function Historico({ onToast }) {
  const [items, setItems] = useState(null);

  useEffect(() => {
    api("/predictions/history")
      .then(setItems)
      .catch((err) => onToast(err.message));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  if (items === null) return <div className="cargando">Cargando histórico…</div>;
  if (items.length === 0)
    return (
      <p className="nota">
        Todavía no tenés predicciones finalizadas. Cuando terminen tus partidos, vas a
        verlas acá con su resultado y puntos.
      </p>
    );

  const totalPuntos = items.filter(hasPuntos).reduce((s, i) => s + i.points, 0);

  return (
    <section className="historico">
      <div className="tabla-header">
        <div>
          <h2>Histórico de predicciones</h2>
          <p>
            {items.length} eventos finalizados · {totalPuntos} pts
          </p>
        </div>
      </div>

      <div className="hist-lista">
        {items.map((item, i) => (
          <div
            className="card hist-card"
            key={item.id}
            style={{ animationDelay: `${i * 45}ms` }}
          >
            <div className="hist-top">
              <span
                className="chip-liga"
                style={{ color: COLORES_DEPORTE[item.sport] }}
              >
                {NOMBRES_DEPORTE[item.sport]} · {item.league}
              </span>
              <span className="chip-hora">
                {new Date(item.start_time_utc).toLocaleDateString("es-AR", {
                  day: "2-digit",
                  month: "short",
                  year: "numeric",
                })}
              </span>
            </div>

            <div className="hist-marcadores">
              <div className="hist-col">
                <span className="hist-label">Predicción</span>
                <span className="hist-valor">{prediccion(item)}</span>
              </div>
              <div className="hist-vs">
                <span className="vs-badge">vs</span>
                <span className="hist-equipo">{compartido(item.teams)}</span>
              </div>
              <div className="hist-col">
                <span className="hist-label">Resultado</span>
                <span className="hist-valor">{resultadoReal(item)}</span>
              </div>
            </div>

            <div className="hist-puntos">
              {hasPuntos(item) ? (
                <>
                  <span className={`punto-resultado ${item.points > 0 ? "ok" : "mal"}`}>
                    {item.points > 0 ? `+${item.points} pts` : "0 pts"}
                  </span>
                </>
              ) : (
                <span className="punto-resultado neutro">sin puntuar</span>
              )}
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}