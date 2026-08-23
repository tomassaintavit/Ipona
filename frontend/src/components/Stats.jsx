import { useEffect, useState } from "react";
import { api } from "../api.js";

function CardStats({ titulo, data }) {
  if (!data) return null;
  return (
    <div className="card">
      <h2>{titulo}</h2>
      <div className="stat-linea">
        <span>Aciertos</span>
        <span>
          {data.aciertos}/{data.predicciones}
        </span>
      </div>
      <div className="stat-linea">
        <span>Precisión</span>
        <span>{Math.round(data.precision * 100)}%</span>
      </div>
      <div className="barras">
        <div
          className="barra"
          style={{ width: `${Math.round(data.precision * 100)}%` }}
        />
      </div>
      {data.por_deporte.map((s) => (
        <div className="stat-linea" key={s.sport}>
          <span>{s.sport}</span>
          <span>
            {s.aciertos}/{s.predicciones} ({Math.round(s.precision * 100)}%) ·{" "}
            {s.puntos} pts
          </span>
        </div>
      ))}
      {data.tokens && (
        <div className="stat-linea">
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
      <CardStats titulo="Mis estadísticas" data={me} />
      <CardStats titulo="La IA · ipona-ia" data={llm} />
    </>
  );
}
