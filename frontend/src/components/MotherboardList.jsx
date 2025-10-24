import { useEffect, useState } from "react";

function MotherboardList({ selected, onChange }) {
  const [mobos, setMobos] = useState([]);

  useEffect(() => {
    let url = "http://localhost:8000/api/motherboards/";
    const params = [];
    if (selected.cpu) params.push(`cpu=${selected.cpu}`);
    if (selected.ram) params.push(`ram=${selected.ram}`);
    if (selected.gpu) params.push(`gpu=${selected.gpu}`);
    if (selected.psu) params.push(`psu=${selected.psu}`);
    if (selected.mem) params.push(`mem=${selected.mem}`);
    if (selected.chassis) params.push(`case=${selected.chassis}`)
    if (params.length) url += "?" + params.join("&");
    fetch(url)
      .then((res) => res.json())
      .then((data) => setMobos(data));
  }, [
    selected.cpu,
    selected.ram,
    selected.gpu,
    selected.psu,
    selected.mem,
    selected.chassis
  ]);

  return (
    <div>
      <h4>Motherboard:</h4>
      <ul style={{ listStyle: "none", padding: 0 }}>
        <li
          key="none"
          onClick={() => onChange(null)}
          style={{
            padding: "8px",
            cursor: "pointer",
              background: selected.mobo === null ? "linear-gradient(to right, #4f5f4f 0%, transparent 75%)" : "#242424",
          }}
        >
          Brak
        </li>
        {mobos.map((mobo) => (
          <li
            key={mobo.id}
            onClick={() => onChange(mobo.id)}
            style={{
              padding: "8px",
              borderTop: "1px solid #ccc",
              cursor: "pointer",
              background: selected.mobo === mobo.id ? "linear-gradient(to right, #4f5f4f 0%, transparent 75%)" : "#242424",
            }}
          >
            {mobo.name}
          </li>
        ))}
      </ul>
    </div>
  );
}

export default MotherboardList;
