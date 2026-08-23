import { useEffect, useState } from "react";
import { api } from "../api.js";

export default function Tabla({ onToast }) {
  const [board, setBoard] = useState(null);

  useEffect(() => {
    api("/leaderboard")
      .then(setBoard)
      .catch((err) => onToast(err.message));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  if (board === null) return <div className="cargando">Cargando tabla…</div>;
  if (board.length === 0)
    return <p className="nota">Todavía no hay jugadores en la tabla.</p>;

  const max = Math.max(...board.map((f) => f.total_points), 1);

  return (
    <>
      <table>
        <thead>
          <tr>
            <th>#</th>
            <th>Jugador</th>
            <th>Pts</th>
            <th>Δ</th>
            <th>Preds</th>
          </tr>
        </thead>
        <tbody>
          {board.map((fila) => {
            const medalla = ["🥇", "🥈", "🥉"][fila.position - 1] || fila.position;
            const dif = fila.position === 1 ? null : (fila.total_points - max).toFixed(1);
            return (
              <tr key={fila.username} className={fila.is_llm ? "llm" : ""}>
                <td>{medalla}</td>
                <td>
                  {fila.username}
                  {fila.is_llm ? " 🤖" : ""}
                </td>
                <td>{fila.total_points}</td>
                <td>{dif === null ? "—" : dif}</td>
                <td>{fila.predictions}</td>
              </tr>
            );
          })}
        </tbody>
      </table>
      <p className="nota">Las predicciones se puntúan al finalizar cada partido.</p>
    </>
  );
}
