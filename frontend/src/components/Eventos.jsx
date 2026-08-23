import { useEffect, useState } from "react";
import { api } from "../api.js";

function formatoHora(iso) {
  return new Date(iso).toLocaleString("es-AR", {
    day: "2-digit",
    month: "short",
    hour: "2-digit",
    minute: "2-digit",
  });
}

function FormularioPrediccion({ evento, onGuardada }) {
  const [error, setError] = useState("");

  async function enviar(ev) {
    ev.preventDefault();
    const f = ev.target;
    setError("");
    let body;
    if (evento.sport === "formula_1") {
      const positions = [f.pos0.value, f.pos1.value, f.pos2.value];
      if (new Set(positions).size !== 3) {
        setError("Elegí 3 pilotos distintos");
        return;
      }
      body = { event_id: evento.id, positions };
    } else {
      body = {
        event_id: evento.id,
        home_score: Number(f.home.value),
        away_score: Number(f.away.value),
      };
    }
    try {
      await api("/predictions", { method: "POST", body: JSON.stringify(body) });
      onGuardada();
    } catch (err) {
      setError(err.message);
    }
  }

  const esF1 = evento.sport === "formula_1";
  const pilotos = evento.participants || [];

  return (
    <form onSubmit={enviar}>
      {esF1
        ? [0, 1, 2].map((i) => (
            <select key={i} name={`pos${i}`} required defaultValue="">
              <option value="" disabled>
                {i + 1}°
              </option>
              {pilotos.map((p) => (
                <option key={p} value={p}>
                  {p}
                </option>
              ))}
            </select>
          ))
        : <>
            <input name="home" type="number" min="0" max="99" required />
            <span>–</span>
            <input name="away" type="number" min="0" max="99" required />
          </>}
      <button type="submit">Predecir</button>
      {error && <span className="error inline">{error}</span>}
    </form>
  );
}

export default function Eventos({ onToast }) {
  const [eventos, setCargados] = useState(null);

  async function cargar() {
    try {
      setCargados(await api("/events/today"));
    } catch (err) {
      onToast(err.message);
    }
  }

  useEffect(() => {
    cargar();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  if (eventos === null) return <div className="cargando">Cargando eventos…</div>;
  if (eventos.length === 0)
    return <p className="nota">No hay eventos para predecir hoy. Volvé más tarde.</p>;

  return (
    <div id="eventos-lista">
      {eventos.map((e) => {
        const titulo =
          e.sport === "formula_1"
            ? e.participants?.slice(0, 8).join(", ") || "Gran Premio"
            : `${e.home_team} vs ${e.away_team}`;
        return (
          <div className="card partido" key={e.id}>
            <div className="equipos">{titulo}</div>
            <div className="meta">
              {e.league} · {formatoHora(e.start_time_utc)}
            </div>
            <FormularioPrediccion evento={e} onGuardada={() => onToast("¡Predicción guardada!")} />
          </div>
        );
      })}
    </div>
  );
}
