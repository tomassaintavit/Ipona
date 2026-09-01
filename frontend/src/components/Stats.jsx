import { useEffect, useState } from "react";
import { api } from "../api.js";

function CardStats({ titulo, data, avatar }) {
  if (!data) return null;
  return (
    <div className="card stat-card">
      <div className="stat-cabecera">
        {avatar && <span className="avatar ia pequeño">{avatar}</span>}
        <h2>{titulo}</h2>
      </div>

      <div className="stat-grid">
        <div className="stat-bl">
          <span className="stat-num">{data.aciertos}/{data.predicciones}</span>
          <span className="stat-label">Aciertos</span>
        </div>
        <div className="stat-bl">
          <span className="stat-num">{Math.round(data.precision * 100)}%</span>
          <span className="stat-label">Precisión</span>
        </div>
      </div>

      <div className="barras">
        <div
          className="barra"
          style={{ width: `${Math.round(data.precision * 100)}%` }}
        />
      </div>

      {data.por_deporte.length > 0 && (
        <div className="por-deporte">
          {data.por_deporte.map((s) => (
            <div className="stat-linea" key={s.sport}>
              <span>{s.sport}</span>
              <span>
                {s.aciertos}/{s.predicciones} ({Math.round(s.precision * 100)}%) · {s.puntos} pts
              </span>
            </div>
          ))}
        </div>
      )}

      {data.tokens && (
        <div className="stat-linea tokens">
          <span>Tokens IA</span>
          <span>
            {data.tokens.total} en {data.tokens.llamadas} llamadas
          </span>
        </div>
      )}
    </div>
  );
}

export default function Stats({ onToast }) {
  const [me, setMe] = useState(null);
  const [llm, setLlm] = useState(null);

  useEffect(() => {
    api("/stats/me").then(setMe).catch((err) => onToast(err.message));
    api("/stats/llm").then(setLlm).catch(() => {});
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <>
      <div className="tabla-header">
        <div>
          <h2>Estadísticas</h2>
          <p>Tu historial y el de la IA.</p>
        </div>
      </div>
      <CardStats titulo="Mis estadísticas" data={me} />
      <CardStats titulo="Cris el pulpo Paul · la IA" data={llm} avatar="IA" />
    </>
  );
}