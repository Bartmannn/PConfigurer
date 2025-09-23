import CPUList from "./CPUList";
import GPUList from "./GPUList";
import MotherboardList from "./MotherboardList";
import RAMList from "./RAMList";

function SideBar({ selectedNode, selected, onChange }) {
  return (
    <div 
        className="side-bar"
        style={{
            width: "25vw",
            background: "#242424",
            borderRight: "1px solid #ccc",
            padding: "10px",
        }}
    >
      <div className="details">
        {selectedNode ? (
          <h3>{selectedNode.label}</h3>
        ) : (
          <p>Kliknij węzeł, aby zobaczyć szczegóły</p>
        )}
      </div>

      <div className="list">
        {selectedNode?.id === "CPU" && (
          <CPUList selected={selected} onChange={(id) => onChange("cpu", id)} />
        )}
        {selectedNode?.id === "MOBO" && (
          <MotherboardList selected={selected} onChange={(id) => onChange("mobo", id)} />
        )}
        {selectedNode?.id === "RAM" && (
          <RAMList selected={selected} onChange={(id) => onChange("ram", id)} />
        )}
        {selectedNode?.id === "GPU" && (
          <GPUList selected={selected} onChange={(id) => onChange("gpu", id)} />
        )}
      </div>
    </div>
  );
}

export default SideBar;
