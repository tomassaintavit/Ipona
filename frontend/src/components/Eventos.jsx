import { useEffect, useRef, useState } from "react";
import { api } from "../api.js";

function formatoHora(iso) {
  return new Date(iso).toLocaleString("es-AR", {
    day: "2-digit",
    month: "short",
    hour: "2-digit",
    minute: "2-digit",
  });
}

function FormularioPrediccion({ evento, previa, onGuardada }) {
  const [error, setError] = useState("");
  const esF1 = evento.sport === "formula_1";
  const [home, setHome] = useState(previa?.home_score ?? "");
  const [away, setAway] = useState(previa?.away_score ?? "");
  const [pos, setPos] = useState(previa?.positions ?? ["", "", ""]);
  const dirty = useRef(!previa);

  function body() {
    if (esF1) {
      const positions = [pos[0], pos[1], pos[2]];
      if (positions.some((p) => !p)) return null;
      if (new Set(positions).size !== 3) {
        setError("Elegí 3 pilotos distintos");
        return null;
      }
      return { event_id: evento.id, positions };
    }
    if (home === "" || away === "") return null;
    return { event_id: evento.id, home_score: Number(home), away_score: Number(away) };
  }

  function guardar() {
    const payload = body();
    if (!payload) return;
    setError("");
    api("/predictions", { method: "POST", body: JSON.stringify(payload) })
      .then(onGuardada)
      .catch((err) => setError(err.message));
  }

  useEffect(() => {
    if (!dirty.current) return;
    const t = setTimeout(guardar, 400);
    return () => clearTimeout(t);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [home, away, pos]);

  function marcarEnsuciado(fn) {
    return (e) => {
      dirty.current = true;
      fn(e);
    };
  }

  const pilotos = evento.participants || [];

  return (
    <>
      {previa && (
        <div className="predicha">
          Tu predicción:{" "}
          <strong>
            {esF1
              ? (previa.positions || []).join(" · ")
              : `${previa.home_score} – ${previa.away_score}`}
          </strong>{" "}
          (podés cambiarla)
        </div>
      )}
      <div className="prediccion">
        {esF1
          ? [0, 1, 2].map((i) => (
              <select
                key={i}
                value={pos[i]}
                onChange={marcarEnsuciado((e) =>
                  setPos((p) => p.map((v, j) => (j === i ? e.target.value : v)))
                )}
              >
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
              <input
                type="number"
                min="0"
                max="99"
                value={home}
                placeholder="Local"
                onChange={marcarEnsuciado((e) => setHome(e.target.value))}
              />
              <span>–</span>
              <input
                type="number"
                min="0"
                max="99"
                value={away}
                placeholder="Visitante"
                onChange={marcarEnsuciado((e) => setAway(e.target.value))}
              />
            </>}
        {error && <span className="error inline">{error}</span>}
      </div>
    </>
  );
}

export default function Eventos({ onToast }) {
  const [eventos, setCargados] = useState(null);
  const [previasPorEvento, setPrevias] = useState({});
  const [recarga, setRecarga] = useState(0);

  async function cargar() {
    try {
      const [evs, misPredicciones] = await Promise.all([
        api("/events/today"),
        api("/predictions/my"),
      ]);
      setCargados(evs);
      const mapa = {};
      for (const p of misPredicciones) mapa[p.event_id] = p;
      setPrevias(mapa);
    } catch (err) {
      onToast(err.message);
    }
  }

  useEffect(() => {
    cargar();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [recarga]);

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
            <FormularioPrediccion
              evento={e}
              previa={previasPorEvento[e.id]}
              onGuardada={() => {
                onToast("¡Predicción guardada!");
                setRecarga((n) => n + 1);
              }}
            />
          </div>
        );
      })}
    </div>
  );
}
