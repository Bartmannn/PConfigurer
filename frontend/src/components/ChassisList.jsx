import { useEffect, useState } from "react";

function ChassisList({ selected, onChange }) {
  const [chassis, setChassis] = useState([]);

  useEffect(() => {
    let url = "http://localhost:8000/api/cases/";
    const params = [];
    if (selected.mobo) params.push(`mobo=${selected.mobo}`);
    if (selected.gpu) params.push(`gpu=${selected.gpu}`)
    if (selected.psu) params.push(`psu=${selected.psu}`);
    if (params.length) url += "?" + params.join("&"); 

    fetch(url)
      .then((res) => res.json())
      .then((data) => setChassis(data));
  }, [selected.mobo, selected.psu, selected.gpu]);

  return (
    <div>
      <h4>Obudowy:</h4>
      <ul style={{ listStyle: "none", padding: 0 }}>
        <li
          key="none"
          onClick={() => onChange(null)}
          style={{
            padding: "8px",
            cursor: "pointer",
              background: selected.chassis === null ? "linear-gradient(to right, #4f5f4f 0%, transparent 75%)" : "#242424",
          }}
        >
          Brak
        </li>
        {chassis.map((computerCase) => (
          <li
            key={computerCase.id}
            onClick={() => onChange(computerCase.id)}
            style={{
              padding: "8px",
              borderTop: "1px solid #ccc",
              cursor: "pointer",
              background: selected.chassis === computerCase.id ? "linear-gradient(to right, #4f5f4f 0%, transparent 75%)" : "#242424",
            }}
          >
            {computerCase.name}
          </li>
        ))}
      </ul>
    </div>
  );
}

export default ChassisList;
