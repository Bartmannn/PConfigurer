import { useEffect, useState } from "react";

function CPUList({ selected, onChange }) {
  const [cpus, setCpus] = useState([]);

  useEffect(() => {
    let url = "http://localhost:8000/api/cpus/";
    const params = [];
    if (selected.mobo) params.push(`mobo=${selected.mobo}`);
    if (selected.ram) params.push(`ram=${selected.ram}`);
    if (params.length) url += "?" + params.join("&"); 
    fetch(url)
      .then((res) => res.json())
      .then((data) => setCpus(data));
  }, [selected.mobo, selected.ram]);

  return (
    <div>
      <label>CPU: </label>
      <select
        value={selected.cpu || ""}
        onChange={(e) => onChange(parseInt(e.target.value))}
      >
        <option value="">-- Select CPU --</option>
        {cpus.map((cpu) => (
          <option key={cpu.id} value={cpu.id}>
            {cpu.name}
          </option>
        ))}
      </select>
    </div>
  );
}

export default CPUList;
