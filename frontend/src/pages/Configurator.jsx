import CPUList from "../components/CPUList";
import RAMList from "../components/RAMList";
import MotherboardList from "../components/MotherboardList";
import { useState } from "react";

function Configurator() {
  const [selected, setSelected] = useState({
    cpu: null,
    mobo: null,
    ram: null,
  });

  const updatePart = (key, value) => {
    setSelected((prev) => ({ ...prev, [key]: value }));
  };

  return (
    <div>
      <h1>PC Configurator</h1>
      <CPUList
        selected={selected}
        onChange={(value) => updatePart("cpu", value)}
      />
      <RAMList
        selected={selected}
        onChange={(value) => updatePart("ram", value)}
      />
      <MotherboardList
        selected={selected}
        onChange={(value) => updatePart("mobo", value)}
      />

      <pre>{JSON.stringify(selected, null, 2)}</pre>
    </div>
  );
}

export default Configurator;
