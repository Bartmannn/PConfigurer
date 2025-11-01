import { useEffect, useState } from "react";

function RAMList({ selected, onChange }) {
  const [rams, setRams] = useState([]);

  useEffect(() => {
    let url = "http://localhost:8000/api/rams/";
    const params = [];
    if (selected.mobo) params.push(`mobo=${selected.mobo}`);
    if (selected.cpu) params.push(`cpu=${selected.cpu}`);
    if (params.length) url += "?" + params.join("&");
    fetch(url)
      .then((res) => res.json())
      .then((data) => setRams(data));
  }, [selected.mobo, selected.cpu]);

  return (
    <div>
      <h4>RAM:</h4>
      <ul style={{ listStyle: "none", padding: 0 }}>
        <li
          key="none"
          onClick={() => onChange(null)}
          style={{
            padding: "8px",
            cursor: "pointer",
              background: selected.ram === null ? "linear-gradient(to right, #4f5f4f 0%, transparent 75%)" : "#242424",
          }}
        >
          Brak
        </li>
        {rams.map((ram) => (
          <li
            key={ram.id}
            onClick={() => onChange(ram.id)}
            style={{
              padding: "8px",
              borderTop: "1px solid #ccc",
              cursor: "pointer",
              background: selected.ram === ram.id ? "linear-gradient(to right, #4f5f4f 0%, transparent 75%)" : "#242424",
            }}
          >
            {ram.name}
          </li>
        ))}
      </ul>
    </div>
  );
}

export default RAMList;
