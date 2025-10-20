import { useEffect, useState } from "react";

function PSUList({ selected, onChange }) {
  const [psus, setPsus] = useState([]);

  useEffect(() => {
    let url = "http://localhost:8000/api/psus/";
    const params = [];
    if (selected.mobo) params.push(`mobo=${selected.mobo}`);
    if (selected.gpu) params.push(`gpu=${selected.gpu}`);
    if (selected.cpu) params.push(`cpu=${selected.cpu}`);
    if (params.length) url += "?" + params.join("&"); 

    fetch(url)
      .then((res) => res.json())
      .then((data) => setPsus(data));
  }, [selected.mobo, selected.gpu, selected.cpu]);

  return (
    <div>
      <h4>PSU:</h4>
      <ul style={{ listStyle: "none", padding: 0 }}>
        <li
          key="none"
          onClick={() => onChange(null)}
          style={{
            padding: "8px",
            cursor: "pointer",
              background: selected.psu === null ? "linear-gradient(to right, #4f5f4f 0%, transparent 75%)" : "#242424",
          }}
        >
          Brak
        </li>
        {psus.map((psu) => (
          <li
            key={psu.id}
            onClick={() => onChange(psu.id)}
            style={{
              padding: "8px",
              borderTop: "1px solid #ccc",
              cursor: "pointer",
              background: selected.psu === psu.id ? "linear-gradient(to right, #4f5f4f 0%, transparent 75%)" : "#242424",
            }}
          >
            {psu.name}
          </li>
        ))}
      </ul>
    </div>
  );
}

export default PSUList;
