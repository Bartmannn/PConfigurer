import { useEffect, useState } from "react";

function MotherboardList({ selected, onChange }) {
  const [mobos, setMobos] = useState([]);

  useEffect(() => {
    let url = "http://localhost:8000/api/motherboards/";
    const params = [];
    if (selected.cpu) params.push(`cpu=${selected.cpu}`);
    if (selected.ram) params.push(`ram=${selected.ram}`);
    if (params.length) url += "?" + params.join("&");
    fetch(url)
      .then((res) => res.json())
      .then((data) => setMobos(data));
  }, [selected.cpu, selected.ram]);

  return (
    <div>
      <label>Motherboard: </label>
      <select
        value={selected.mobo || ""}
        onChange={(e) => onChange(parseInt(e.target.value))}
      >
        <option value="">-- Select Motherboard --</option>
        {mobos.map((mobo) => (
          <option key={mobo.id} value={mobo.id}>
            {mobo.name}
          </option>
        ))}
      </select>
    </div>
  );
}

export default MotherboardList;
