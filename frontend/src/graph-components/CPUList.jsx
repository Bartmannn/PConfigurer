import { useEffect, useState } from "react";

function CPUList({ selected, onChange }) {
  const [cpus, setCpus] = useState([]);

  useEffect(() => {
    let url = "http://localhost:8000/api/cpus/";
    const params = [];
    if (selected.mobo) params.push(`mobo=${selected.mobo}`);
    if (selected.ram) params.push(`ram=${selected.ram}`);
    if (selected.gpu) params.push(`gpu=${selected.gpu}`);
    if (selected.psu) params.push(`psu=${selected.psu}`);
    if (params.length) url += "?" + params.join("&"); 

    fetch(url)
      .then((res) => res.json())
      .then((data) => setCpus(data));
  }, [selected.mobo, selected.ram, selected.psu, selected.gpu]);

  return (
    <div>
      <h4>CPU:</h4>
      <ul style={{ listStyle: "none", padding: 0 }}>
        <li
          key="none"
          onClick={() => onChange(null)}
          style={{
            padding: "8px",
            cursor: "pointer",
              background: selected.cpu === null ? "linear-gradient(to right, #4f5f4f 0%, transparent 75%)" : "#242424",
          }}
        >
          Brak
        </li>
        {cpus.map((cpu) => (
          <li
            key={cpu.id}
            onClick={() => onChange(cpu.id)}
            style={{
              padding: "8px",
              borderTop: "1px solid #ccc",
              cursor: "pointer",
              background: selected.cpu === cpu.id ? "linear-gradient(to right, #4f5f4f 0%, transparent 75%)" : "#242424",
            }}
          >
            {cpu.name}
          </li>
        ))}
      </ul>
    </div>
  );
}

export default CPUList;
