import React, { useState } from "react";
import GraphView from "./components/GraphView";
import SideBar from "./components/SideBar";

function App() {
  const [selectedNode, setSelectedNode] = useState(null);

  const [selected, setSelected] = useState({
    cpu: null,
    mobo: null,
    ram: null,
    gpu: null,
  });

  const handleComponentChange = (type, id) => {
    setSelected((prev) => ({ ...prev, [type]: id }));
  };

  return (
    <div style={{ display: "flex", height: "100vh" }}>
      <SideBar
        selectedNode={selectedNode}
        selected={selected}
        onChange={handleComponentChange}
      />
      <GraphView
        selected={selected}
        onNodeSelect={setSelectedNode}
      />
    </div>
  );
}

export default App;
