import { useRef, useState } from "react";
import { api } from "../api.js";

const BIENVENIDA = {
  role: "assistant",
  content:
    "¡Hola! Soy Cris el pulpo Paul 🐙, el pulpo adivino de ipOna. Predigo los partidos y también te puedo responder cosas del juego:\n" +
    "· ¿Cómo salió Racing en sus últimos partidos?\n" +
    "· ¿Cómo va la tabla?\n" +
    "· ¿Qué predije últimamente?\n" +
    "· ¿Qué partidos hay próximos?\n" +
    "· ¿Cómo se puntúan las predicciones?",
};

export default function ChatWidget() {
  const [abierto, setAbierto] = useState(false);
  const [mensajes, setMensajes] = useState([BIENVENIDA]);
  const [enviando, setEnviando] = useState(false);
  const inputRef = useRef(null);

  async function enviar(ev) {
    ev.preventDefault();
    const texto = inputRef.current.value.trim();
    if (!texto || enviando) return;
    inputRef.current.value = "";

    const historial = mensajes
      .filter((m) => m !== BIENVENIDA)
      .slice(-10)
      .map((m) => ({ role: m.role, content: m.content }));

    setMensajes((prev) => [...prev, { role: "user", content: texto }]);
    setEnviando(true);
    try {
      const res = await api("/chat", {
        method: "POST",
        body: JSON.stringify({ mensaje: texto, historial }),
      });
      setMensajes((prev) => [...prev, { role: "assistant", content: res.respuesta }]);
    } catch (err) {
      setMensajes((prev) => [
        ...prev,
        { role: "assistant", content: `⚠️ ${err.message}` },
      ]);
    } finally {
      setEnviando(false);
    }
  }

  return (
    <>
      {abierto && (
        <div className="chat-panel">
          <div className="chat-header">
            <span className="roboto">CP3</span>
            <button className="chat-cerrar" onClick={() => setAbierto(false)}>
              ✕
            </button>
          </div>
          <div className="chat-mensajes">
            {mensajes.map((m, i) => (
              <div key={i} className={`burbuja ${m.role}`}>
                {m.content}
              </div>
            ))}
            {enviando && (
              <div className="burbuja assistant escribiendo">escribiendo…</div>
            )}
          </div>
          <form className="chat-input" onSubmit={enviar}>
            <input
              ref={inputRef}
              placeholder="Preguntá algo…"
              maxLength={1000}
              autoComplete="off"
            />
            <button type="submit" disabled={enviando}>
              Enviar
            </button>
          </form>
        </div>
      )}
      {!abierto && (
        <button
          className="chat-fab"
          onClick={() => setAbierto(true)}
          aria-label="Abrir asistente"
        >
          <img src="/assets/logo.png" alt="" />
        </button>
      )}
    </>
  );
}
