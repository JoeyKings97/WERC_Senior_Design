import { useEffect, useState } from "react";

const WS_URL = "ws://127.0.0.1:8000/ws/telemetry";
const API_URL = "http://127.0.0.1:8000";

export default function App() {
  const [latest, setLatest] = useState({});
  const [pumpEnabled, setPumpEnabled] = useState(false);

  useEffect(() => {
    const socket = new WebSocket(WS_URL);
    socket.onmessage = (event) => {
      const data = JSON.parse(event.data);
      setLatest(data);
    };
    socket.onerror = () => socket.close();
    return () => socket.close();
  }, []);

  const toggleControl = async (enable) => {
    setPumpEnabled(enable);
    await fetch(`${API_URL}/control/${enable ? "enable" : "disable"}`, {
      method: "POST",
    });
  };

  return (
    <>
      <header>
        <h2>Cooling Tower Water Recovery Dashboard</h2>
        <p>Live telemetry + manual control</p>
      </header>
      <main>
        <section className="card">
          <h3>Controls</h3>
          <div className="controls">
            <button onClick={() => toggleControl(true)}>Enable Control</button>
            <button className="secondary" onClick={() => toggleControl(false)}>
              Disable Control
            </button>
            <span>Status: {pumpEnabled ? "Enabled" : "Disabled"}</span>
          </div>
        </section>
        <section className="card">
          <h3>KPIs</h3>
          <div className="kpis">
            <Kpi label="Humidity (%)" value={latest.humidity} />
            <Kpi label="Temp (°C)" value={latest.temperature} />
            <Kpi label="Airflow (m/s)" value={latest.airflow} />
            <Kpi label="Condensate (L/h)" value={latest.condensate_rate} />
            <Kpi label="Pump" value={latest.pump_status ? "On" : "Off"} />
          </div>
        </section>
        <section className="card">
          <h3>Raw Telemetry</h3>
          <pre>{JSON.stringify(latest, null, 2)}</pre>
        </section>
      </main>
    </>
  );
}

function Kpi({ label, value }) {
  return (
    <div className="kpi">
      <div style={{ opacity: 0.8, fontSize: "0.9rem" }}>{label}</div>
      <div style={{ fontSize: "1.4rem", fontWeight: 700 }}>{value ?? "—"}</div>
    </div>
  );
}
