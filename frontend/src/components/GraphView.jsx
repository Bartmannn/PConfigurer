import React from "react";
import ForceGraph2D from "react-force-graph-2d";

const GraphView = ({ selected, onNodeSelect }) => {
  const data = {
    nodes: [
      { id: "CPU", label: "CPU", fx: 100, fy: -100 },
      { id: "MOBO", label: "Płyta główna", fx: 0, fy: 0 },
      { id: "RAM", label: "RAM", fx: 100, fy: 100 },
    //   { id: "PSU", label: "PSU", fx: 100, fy: 100 },
    //   { id: "MEM", label: "Dysk", fx: 100, fy: 100 },
      { id: "GPU", label: "GPU", fx: 150, fy: 150 },
    //   { id: "Case", label: "Obudowa", fx: 100, fy: 100 },
    //   { id: "Cool", label: "Chłodzenie", fx: 100, fy: 100 },
    ],
    links: [
      { source: "CPU", target: "MOBO", color: "gray" },
      { source: "RAM", target: "MOBO", color: "gray" },
      { source: "RAM", target: "CPU", color: "gray" },
      // { srouce: "GPU", target: "MOBO", color: "gray" },
    ],
  };

  return (
    <ForceGraph2D
      graphData={data}
      linkWidth={4}
      nodeRelSize={40}
      nodeCanvasObject={(node, ctx) => {
        // zmiana koloru węzła jeśli wybrany komponent istnieje
        const isSelected = selected[node.id.toLowerCase()];
        ctx.fillStyle = isSelected ? "lightgreen" : "lightblue";

        ctx.beginPath();
        ctx.arc(node.x, node.y, 40, 0, 2 * Math.PI, false);
        ctx.fill();
        ctx.stroke();

        // nazwa
        ctx.fillStyle = "black";
        ctx.font = "12px Sans-Serif";
        ctx.textAlign = "center";
        ctx.fillText(node.label, node.x, node.y - 4);

        // plus
        ctx.fillStyle = "darkgreen";
        ctx.font = "18px Sans-Serif";
        ctx.fillText("+", node.x, node.y + 16);
      }}
      linkColor={(link) => link.color}
      onNodeClick={onNodeSelect}
    />
  );
};

export default GraphView;
