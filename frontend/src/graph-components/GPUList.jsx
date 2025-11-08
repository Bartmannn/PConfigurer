import { useEffect, useState } from "react";

function GPUList({ selected, onChange }) {
  const [gpus, setGpus] = useState([]);

  useEffect(() => { //TODO: uprościć tworzenie paramów
    let url = "http://localhost:8000/api/gpus/";
    const params = [];
    if (selected.psu) params.push(`psu=${selected.psu}`);
    if (selected.cpu) params.push(`cpu=${selected.cpu}`);
    if (selected.mobo) params.push(`mobo=${selected.mobo}`);
    if (selected.chassis) params.push(`case=${selected.chassis}`)
    if (params.length) url += "?" + params.join("&"); 

    fetch(url)
      .then((res) => res.json())
      .then((data) => setGpus(data));
  }, [
    selected.psu,
    selected.cpu,
    selected.mobo,
    selected.chassis
  ]);

  return (
    <div>
      <h4>GPU:</h4>
      <ul style={{ listStyle: "none", padding: 0 }}>
        <li
          key="none"
          onClick={() => onChange(null)}
          style={{
            padding: "8px",
            cursor: "pointer",
              background: selected.gpu === null ? "linear-gradient(to right, #4f5f4f 0%, transparent 75%)" : "#242424",
          }}
        >
          Brak
        </li>
        {
        gpus.map((gpu) => (
          <li
            key={gpu.id}
            onClick={() => onChange(gpu.id)}
            style={{
              padding: "8px",
              borderTop: "1px solid #ccc",
              cursor: "pointer",
              background: selected.gpu === gpu.id ? "linear-gradient(to right, #4f5f4f 0%, transparent 75%)" : "transparent",
            }}
          >
            {gpu.display_name}
          </li>
        ))}
      </ul>
    </div>
  );
}

export default GPUList;
