import { useEffect, useRef, useState } from "react";
import { getToken, setToken } from "./api.js";
import Header from "./components/Header.jsx";
import AuthLogin from "./components/AuthLogin.jsx";
import AuthRegistro from "./components/AuthRegistro.jsx";
import Eventos from "./components/Eventos.jsx";
import ChatWidget from "./components/ChatWidget.jsx";
import Tabla from "./components/Tabla.jsx";
import Historico from "./components/Historico.jsx";
import Stats from "./components/Stats.jsx";

export default function App() {
  const [logueado, setLogueado] = useState(Boolean(getToken()));
  const [vista, setVista] = useState("eventos");
  const [toast, setToast] = useState("");
  const timer = useRef(null);

  function showToast(msg) {
    setToast(msg);
    clearTimeout(timer.current);
    timer.current = setTimeout(() => setToast(""), 2500);
  }

  function handleLogin(token) {
    if (typeof token === "string") setToken(token);
    setLogueado(true);
    setVista("eventos");
  }

  function handleLogout() {
    setToken(null);
    setLogueado(false);
  }

  useEffect(() => {
    return () => clearTimeout(timer.current);
  }, []);

  if (!logueado) {
    const authActual = vista.startsWith("auth") ? vista : "auth-login";
    return (
      <main>
        {authActual === "auth-registro" ? (
          <AuthRegistro onLogin={handleLogin} />
        ) : (
          <AuthLogin onLogin={handleLogin} irARegistro={() => setVista("auth-registro")} />
        )}
        {toast && <div id="toast">{toast}</div>}
      </main>
    );
  }

  return (
    <>
      <Header vista={vista} onVista={setVista} onLogout={handleLogout} />
      <main>
        {vista === "eventos" && <Eventos onToast={showToast} />}
        {vista === "tabla" && <Tabla onToast={showToast} />}
        {vista === "historico" && <Historico onToast={showToast} />}
        {vista === "stats" && <Stats onToast={showToast} />}
      </main>
      <ChatWidget />
      {toast && <div id="toast">{toast}</div>}
    </>
  );
}
