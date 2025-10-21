import { useEffect, useState } from "react";

function MemoryList({ selected, onChange }) {
  const [mems, setMem] = useState([]);

  useEffect(() => { //TODO: uprościć tworzenie paramów
    let url = "http://localhost:8000/api/mems/";
    const params = [];
    if (selected.mobo) params.push(`mobo=${selected.mobo}`);
    // if (selected.psu) params.push(`psu=${selected.psu}`);
    // if (selected.cpu) params.push(`cpu=${selected.cpu}`)
    if (params.length) url += "?" + params.join("&"); 

    fetch(url)
      .then((res) => res.json())
      .then((data) => setMem(data));
  }, [selected.mobo]);

  return (
    <div>
      <h4>Pamięć:</h4>
      <ul style={{ listStyle: "none", padding: 0 }}>
        <li
          key="none"
          onClick={() => onChange(null)}
          style={{
            padding: "8px",
            cursor: "pointer",
              background: selected.mem === null ? "linear-gradient(to right, #4f5f4f 0%, transparent 75%)" : "#242424",
          }}
        >
          Brak
        </li>
        {
        mems.map((mem) => (
          <li
            key={mem.id}
            onClick={() => onChange(mem.id)}
            style={{
              padding: "8px",
              borderTop: "1px solid #ccc",
              cursor: "pointer",
              background: selected.mem === mem.id ? "linear-gradient(to right, #4f5f4f 0%, transparent 75%)" : "transparent",
            }}
          >
            {mem.name}
          </li>
        ))}
      </ul>
    </div>
  );
}

export default MemoryList;
