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

function cuandoEmpieza(iso) {
  const diff = new Date(iso) - Date.now();
  if (diff < 0) return "finalizado";
  const min = Math.round(diff / 60000);
  if (min < 1) return "en menos de 1 min";
  if (min < 60) return `en ${min} min`;
  const h = Math.floor(min / 60);
  const m = min % 60;
  return m ? `en ${h}h ${m}m` : `en ${h}h`;
}

function FormularioPrediccion({ evento, previa, onGuardada }) {
  const [error, setError] = useState("");
  const [estado, setEstado] = useState("");
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
    setEstado("guardando");
    api("/predictions", { method: "POST", body: JSON.stringify(payload) })
      .then(() => {
        setEstado("guardado");
        onGuardada();
      })
      .catch((err) => {
        setError(err.message);
        setEstado("");
      });
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
          </strong>
          <span className="editar">podés cambiarla</span>
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
                className="marcador"
                type="number"
                min="0"
                max="99"
                value={home}
                placeholder="Local"
                onChange={marcarEnsuciado((e) => setHome(e.target.value))}
              />
              <span className="sep">–</span>
              <input
                className="marcador"
                type="number"
                min="0"
                max="99"
                value={away}
                placeholder="Visitante"
                onChange={marcarEnsuciado((e) => setAway(e.target.value))}
              />
            </>}
        {estado === "guardando" && <span className="estado-guardado guardando">Guardando…</span>}
        {estado === "guardado" && <span className="estado-guardado guardado">Guardado</span>}
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
      <div className="tabla-header">
        <div>
          <h2>Eventos de hoy</h2>
          <p>Predicé y ganá puntos.</p>
        </div>
        <span className="chip-vivos">{eventos.length} eventos</span>
      </div>

      {eventos.map((e) => {
        const onGuardada = () => {
          onToast("¡Predicción guardada!");
          setRecarga((n) => n + 1);
        };
        return (
          <div className="card evento" key={e.id}>
            <div className="evento-top">
              <span className="chip-liga">{e.league}</span>
              <span className={`chip-hora${new Date(e.start_time_utc) < Date.now() ? " pasada" : ""}`}>
                {formatoHora(e.start_time_utc)} · {cuandoEmpieza(e.start_time_utc)}
              </span>
            </div>

            {e.sport === "formula_1" ? (
              <>
                <p className="evento-titulo f1">¿Quién llega al podio?</p>
                <div className="pilotos">
                  {e.participants?.map((p) => (
                    <span className="chip-piloto" key={p}>
                      {p}
                    </span>
                  ))}
                </div>
              </>
            ) : (
              <div className="vs">
                <span className="equipo">{e.home_team}</span>
                <span className="vs-badge">VS</span>
                <span className="equipo">{e.away_team}</span>
              </div>
            )}

            <FormularioPrediccion
              evento={e}
              previa={previasPorEvento[e.id]}
              onGuardada={onGuardada}
            />
          </div>
        );
      })}
    </div>
  );
}