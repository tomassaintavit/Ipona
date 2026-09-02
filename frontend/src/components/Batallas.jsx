import { useEffect, useState } from "react";
import { api } from "../api.js";

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

const COLORES_AVATAR = ["#6d4ba3", "#8b5cf6", "#a582d4", "#5b21b6", "#c084fc"];

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

function formatoFecha(iso) {
  const d = new Date(iso + "T00:00:00");
  return d.toLocaleDateString("es-AR", { weekday: "short", day: "numeric", month: "short" });
}

export default function Batallas({ onToast }) {
  const [hoy, setHoy] = useState(null);
  const [semana, setSemana] = useState([]);
  const [mensaje, setMensaje] = useState("");
  const [cargando, setCargando] = useState(true);

  function cargar() {
    Promise.all([api("/battles/today"), api("/battles/week")])
      .then(([h, s]) => {
        setHoy(h);
        setSemana(s);
      })
      .catch((err) => onToast(err.message))
      .finally(() => setCargando(false));
  }

  useEffect(() => {
    cargar();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  function enviarMensaje() {
    if (!hoy || mensaje.trim() === "") return;
    api("/battles/message", {
      method: "POST",
      body: JSON.stringify({ battle_id: hoy.battle_id, message: mensaje.trim() }),
    })
      .then(setHoy)
      .then(() => cargar())
      .catch((err) => onToast(err.message));
  }

  if (cargando) return <div className="cargando">Cargando batallas…</div>;

  return (
    <section className="batallas">
      <h2>Batallas</h2>

      {hoy ? (
        <div className={`battle-tarjeta ${hoy.winner ? "resuelta" : ""}`}>
          <div className="battle-titulo">
            <span className="chip-batalla">Hoy</span>
            {hoy.is_trio && <span className="chip-trio">Trío</span>}
          </div>
          <div className="battle-vs">
            <div className="battle-lado">
              <Avatar nombre="tú" ia={false} />
              <span className="battle-nombre">Tú</span>
              <span className="battle-pts">{hoy.my_points ?? "—"} pts</span>
            </div>
            <div className="battle-vs-label">VS</div>
            <div className="battle-lado">
              <Avatar nombre={hoy.opponent.username} ia={hoy.opponent.is_llm} />
              <span className="battle-nombre">
                {hoy.opponent.username}
                {hoy.opponent.is_llm && <span className="chip-ia">IA</span>}
              </span>
              <span className="battle-pts">{hoy.opponent_points ?? "—"} pts</span>
            </div>
          </div>

          {hoy.status === "pendiente" && (
            <p className="nota">
              La batalla se define cuando se puntúen todos los partidos del día.
            </p>
          )}

          {hoy.status === "resuelta" && (
            <div className="battle-resultado">
              <p>
                {hoy.winner === "me"
                  ? "¡Ganaste! Escribile un mensaje a " + hoy.opponent.username + "."
                  : hoy.winner === "opponent"
                  ? "Ganó " +
                    hoy.opponent.username +
                    (hoy.opponent.is_llm ? " (IA)" : "") +
                    "."
                  : "Empate. Nadie escribe."}
              </p>
              {hoy.winner === "me" && hoy.winner_message ? (
                <div className="battle-mensaje-enviado">
                  Tu mensaje: “{hoy.winner_message}”
                </div>
              ) : null}
              {hoy.winner === "me" && !hoy.winner_message ? (
                <form
                  className="battle-form"
                  onSubmit={(e) => {
                    e.preventDefault();
                    enviarMensaje();
                  }}
                >
                  <input
                    value={mensaje}
                    maxLength={100}
                    placeholder="Escribí tu mensaje (máx. 100 caracteres)"
                    onChange={(e) => setMensaje(e.target.value)}
                  />
                  <button type="submit" disabled={mensaje.trim() === ""}>
                    Enviar
                  </button>
                </form>
              ) : null}
              {hoy.winner === "opponent" && hoy.winner_message ? (
                <div className="battle-mensaje-recibido">
                  Te escribió: “{hoy.winner_message}”
                </div>
              ) : null}
            </div>
          )}
        </div>
      ) : (
        <p className="nota">
          No tenés batalla de hoy. Se crean cada mañana a las 6:00 UTC; si te registraste
          hoy, empezás mañana.
        </p>
      )}

      {semana.length > 0 && (
        <div className="battle-historico">
          <h3>Esta semana</h3>
          <ul>
            {semana.map((b, i) => (
              <li key={i}>
                <span className="battle-fecha">{formatoFecha(b.battle_date)}</span>
                <span className="battle-resumen">
                  vs {b.opponent.username}
                  {b.opponent.is_llm ? " (IA)" : ""}
                </span>
                <span className={`battle-estado est-${b.result || "pendiente"}`}>
                  {b.result === "gane" ? "ganaste" : b.result === "perdi" ? "perdiste" : b.result === "empate" ? "empate" : "pendiente"}
                </span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </section>
  );
}
