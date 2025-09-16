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
      <label>RAM: </label>
      <select
        value={selected.ram || ""}
        onChange={(e) => onChange(parseInt(e.target.value))}
      >
        <option value="">-- Select RAM --</option>
        {rams.map((ram) => (
          <option key={ram.id} value={ram.id}>
            {ram.name}
          </option>
        ))}
      </select>
    </div>
  );
}

export default RAMList;
