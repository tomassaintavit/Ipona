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

function AvatarChat({ role }) {
  if (role === "assistant") {
    return (
      <div className="avatar-chat ia">
        <img src="/assets/logo.png" alt="Cris" />
      </div>
    );
  }
  return <div className="avatar-chat">yo</div>;
}

function Cierre() {
  return (
    <svg viewBox="0 0 24 24" width="16" height="16" fill="currentColor" aria-hidden="true">
      <path d="M18.3 5.71a1 1 0 0 0-1.41 0L12 10.59 7.11 5.7a1 1 0 0 0-1.41 1.41L10.59 12l-4.89 4.89a1 1 0 1 0 1.41 1.41L12 13.41l4.89 4.89a1 1 0 0 0 1.41-1.41L13.41 12l4.89-4.89a1 1 0 0 0 0-1.4z" />
    </svg>
  );
}

function EnviarIcono() {
  return (
    <svg viewBox="0 0 24 24" width="17" height="17" fill="currentColor" aria-hidden="true">
      <path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z" />
    </svg>
  );
}

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
            <div className="chat-titulo">
              <div className="avatar-chat ia chico">
                <img src="/assets/logo.png" alt="Cris" />
              </div>
              <div>
                <span className="chat-nombre">Cris el pulpo Paul</span>
                <span className="chat-estado">
                  <i /> en línea
                </span>
              </div>
            </div>
            <button className="chat-cerrar" onClick={() => setAbierto(false)} aria-label="Cerrar chat">
              <Cierre />
            </button>
          </div>

          <div className="chat-mensajes">
            <p className="chat-note">
              Preguntame por partidos, tu tabla o cómo se puntúa.
            </p>
            {mensajes.map((m, i) => (
              <div className="chat-fila" key={i}>
                <AvatarChat role={m.role} />
                <div className={`burbuja ${m.role}`}>{m.content}</div>
              </div>
            ))}
            {enviando && (
              <div className="chat-fila">
                <div className="avatar-chat ia">
                  <img src="/assets/logo.png" alt="Cris" />
                </div>
                <div className="burbuja assistant escribiendo">
                  <span className="puntos">
                    <i />
                    <i />
                    <i />
                  </span>
                  <span className="sr-only">escribiendo…</span>
                </div>
              </div>
            )}
          </div>

          <form className="chat-input" onSubmit={enviar}>
            <input
              ref={inputRef}
              placeholder="Preguntá algo…"
              maxLength={1000}
              autoComplete="off"
            />
            <button type="submit" disabled={enviando} aria-label="Enviar">
              <EnviarIcono />
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